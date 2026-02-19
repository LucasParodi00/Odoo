# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class AppointmentWizard(models.TransientModel):
    _name = 'appointment.wizard'
    _description = 'Wizard de Solicitud de Turno'

    # Especialidad y Médico
    specialty_id = fields.Many2one(
        'medical.specialty',
        string='Especialidad',
        required=True,
        help='Seleccione la especialidad médica requerida'
    )
    
    doctor_id = fields.Many2one(
        'res.partner',
        string='Médico',
        domain="[('id', 'in', available_doctor_ids)]",
        help='Seleccione el médico'
    )
    available_doctor_ids = fields.Many2many(
        'res.partner',
        compute='_compute_available_doctors',
        string='Médicos Disponibles'
    )
    
    # Fecha y Slot
    date_from = fields.Date(
        string='Fecha Desde',
        default=lambda self: fields.Date.today(),
        required=True
    )
    date_to = fields.Date(
        string='Fecha Hasta',
        compute='_compute_date_to',
        store=True,
        readonly=False,
        required=True
    )
    slot_id = fields.Many2one(
        'appointment.slot',
        string='Horario',
        domain="[('id', 'in', available_slot_ids), ('state', '=', 'available')]"
    )
    available_slot_ids = fields.Many2many(
        'appointment.slot',
        compute='_compute_available_slots',
        string='Slots Disponibles'
    )
    
    # Paciente
    patient_type = fields.Selection([
        ('human', 'Humano'),
        ('pet', 'Mascota')
    ], string='Tipo de Paciente', default='human', required=True)
    
    patient_id = fields.Many2one(
        'res.partner',
        string='Paciente',
        domain=[('is_patient', '=', True)]
    )
    pet_id = fields.Many2one(
        'medical.patient.pet',
        string='Mascota'
    )
    
    # Información adicional
    notes = fields.Text(string='Notas')

    @api.depends('date_from')
    def _compute_date_to(self):
        for wizard in self:
            if wizard.date_from:
                wizard.date_to = wizard.date_from + timedelta(days=30)
            else:
                wizard.date_to = fields.Date.today() + timedelta(days=30)

    @api.depends('specialty_id')
    def _compute_available_doctors(self):
        for wizard in self:
            if wizard.specialty_id:
                # Buscar médicos que atienden esta especialidad
                doctor_specialties = self.env['medical.doctor.specialty'].search([
                    ('specialty_id', '=', wizard.specialty_id.id),
                    ('active', '=', True)
                ])
                wizard.available_doctor_ids = doctor_specialties.mapped('doctor_id')
            else:
                wizard.available_doctor_ids = False

    @api.depends('specialty_id', 'doctor_id', 'date_from', 'date_to')
    def _compute_available_slots(self):
        for wizard in self:
            if wizard.specialty_id and wizard.date_from and wizard.date_to:
                # Obtener o generar slots disponibles
                slots = self.env['appointment.slot'].get_available_slots(
                    specialty_id=wizard.specialty_id.id,
                    doctor_id=wizard.doctor_id.id if wizard.doctor_id else None,
                    start_date=wizard.date_from,
                    end_date=wizard.date_to
                )
                wizard.available_slot_ids = slots
            else:
                wizard.available_slot_ids = False

    @api.onchange('specialty_id')
    def _onchange_specialty_id(self):
        """Al cambiar especialidad, limpiar médico y slot"""
        self.doctor_id = False
        self.slot_id = False

    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        """Al cambiar médico, limpiar slot"""
        self.slot_id = False

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        """Al cambiar fechas, limpiar slot"""
        self.slot_id = False

    def action_create_appointment(self):
        """Crear el turno"""
        self.ensure_one()
        
        # Validaciones
        if not self.specialty_id:
            raise UserError(_('Debe seleccionar una especialidad'))
        
        if not self.doctor_id:
            raise UserError(_('Debe seleccionar un médico'))
        
        if not self.slot_id:
            raise UserError(_('Debe seleccionar un horario'))
        
        if self.patient_type == 'human' and not self.patient_id:
            raise UserError(_('Debe seleccionar un paciente'))
        elif self.patient_type == 'pet' and not self.pet_id:
            raise UserError(_('Debe seleccionar una mascota'))
        
        # Verificar que el slot esté disponible
        if self.slot_id.state != 'available':
            raise UserError(_('El horario seleccionado ya no está disponible'))
        
        # Crear el turno
        appointment_vals = {
            'slot_id': self.slot_id.id,
            'patient_type': self.patient_type,
            'notes': self.notes or '',
        }
        
        if self.patient_type == 'human':
            appointment_vals['patient_id'] = self.patient_id.id
        else:
            appointment_vals['pet_id'] = self.pet_id.id
        
        try:
            appointment = self.env['medical.appointment'].create(appointment_vals)
            
            # Mostrar el turno creado
            return {
                'type': 'ir.actions.act_window',
                'name': _('Turno Creado'),
                'res_model': 'medical.appointment',
                'res_id': appointment.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {'form_view_initial_mode': 'readonly'},
            }
        except Exception as e:
            raise UserError(_('Error al crear el turno: %s') % str(e))
