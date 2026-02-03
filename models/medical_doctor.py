# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalDoctor(models.Model):
    """
    Médicos - Profesionales que brindan atención médica.
    Vinculados a res.partner y con una o varias especialidades.
    """
    _name = 'medical.doctor'
    _description = 'Médico'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto',
        required=True,
        ondelete='restrict',
        tracking=True,
        help='Contacto asociado al médico'
    )
    
    name = fields.Char(
        string='Nombre',
        related='partner_id.name',
        store=True,
        readonly=True
    )
    
    license_number = fields.Char(
        string='Número de Matrícula',
        tracking=True,
        help='Número de matrícula profesional'
    )
    
    specialty_ids = fields.Many2many(
        'medical.specialty',
        'medical_specialty_doctor_rel',
        'doctor_id',
        'specialty_id',
        string='Especialidades',
        required=True,
        tracking=True,
        help='Especialidades que atiende el médico'
    )
    
    def write(self, vals):
        """Sobrescribir write para crear agendas cuando se agregan especialidades"""
        result = super().write(vals)
        
        # Si se modificaron las especialidades, crear agendas faltantes
        if 'specialty_ids' in vals:
            for doctor in self:
                for specialty in doctor.specialty_ids:
                    # Verificar si ya existe una agenda para esta especialidad
                    existing = self.env['medical.schedule'].search([
                        ('doctor_id', '=', doctor.id),
                        ('specialty_id', '=', specialty.id)
                    ], limit=1)
                    
                    if not existing:
                        self.env['medical.schedule'].create({
                            'name': f'Agenda {specialty.name} - {doctor.partner_id.name}',
                            'doctor_id': doctor.id,
                            'specialty_id': specialty.id,
                            'active': True,
                        })
        
        return result
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True
    )
    
    color = fields.Integer(
        string='Color',
        help='Color para identificación visual en calendarios'
    )
    
    notes = fields.Text(
        string='Notas'
    )
    
    # Agenda
    schedule_ids = fields.One2many(
        'medical.schedule',
        'doctor_id',
        string='Agendas'
    )
    
    current_schedule_id = fields.Many2one(
        'medical.schedule',
        string='Agenda Actual',
        help='Agenda activa del médico',
        compute='_compute_current_schedule',
        store=True
    )
    
    # Relaciones
    appointment_ids = fields.One2many(
        'medical.appointment',
        'doctor_id',
        string='Turnos'
    )
    
    clinical_history_ids = fields.One2many(
        'medical.clinical.history',
        'doctor_id',
        string='Historias Clínicas'
    )
    
    # Contadores
    specialty_count = fields.Integer(
        string='Cantidad de Especialidades',
        compute='_compute_specialty_count'
    )
    
    appointment_count = fields.Integer(
        string='Cantidad de Turnos',
        compute='_compute_appointment_count'
    )
    
    @api.depends('specialty_ids')
    def _compute_specialty_count(self):
        for doctor in self:
            doctor.specialty_count = len(doctor.specialty_ids)
    
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for doctor in self:
            doctor.appointment_count = len(doctor.appointment_ids)
    
    def action_view_appointments(self):
        """Acción para ver turnos de este médico"""
        self.ensure_one()
        return {
            'name': 'Turnos',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.appointment',
            'view_mode': 'list,form,calendar',
            'domain': [('doctor_id', '=', self.id)],
            'context': {'default_doctor_id': self.id}
        }
    
    def action_view_schedules(self):
        """Acción para ver agendas de este médico"""
        self.ensure_one()
        return {
            'name': 'Agendas',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.schedule',
            'view_mode': 'list,form',
            'domain': [('doctor_id', '=', self.id)],
            'context': {'default_doctor_id': self.id}
        }
    
    @api.depends('schedule_ids', 'schedule_ids.active')
    def _compute_current_schedule(self):
        """Obtiene la primera agenda activa (deprecado - usar get_schedule_for_specialty)"""
        for doctor in self:
            active_schedule = doctor.schedule_ids.filtered(lambda s: s.active)
            doctor.current_schedule_id = active_schedule[0] if active_schedule else False
    
    def get_schedule_for_specialty(self, specialty_id):
        """Obtiene la agenda activa para una especialidad específica"""
        self.ensure_one()
        return self.schedule_ids.filtered(
            lambda s: s.active and s.specialty_id.id == specialty_id
        )
    
    @api.constrains('license_number')
    def _check_license_number(self):
        for doctor in self:
            if doctor.license_number:
                duplicate = self.search([
                    ('id', '!=', doctor.id),
                    ('license_number', '=', doctor.license_number)
                ], limit=1)
                if duplicate:
                    raise ValidationError(
                        _('El número de matrícula %s ya está asignado al Dr./Dra. %s') % 
                        (doctor.license_number, duplicate.name)
                    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Sobrescribir create para asegurar que se cree una agenda por cada especialidad"""
        doctors = super().create(vals_list)
        for doctor in doctors:
            # Crear agenda para cada especialidad del médico
            for specialty in doctor.specialty_ids:
                # Verificar si ya existe una agenda para esta especialidad
                existing = self.env['medical.schedule'].search([
                    ('doctor_id', '=', doctor.id),
                    ('specialty_id', '=', specialty.id)
                ], limit=1)
                
                if not existing:
                    self.env['medical.schedule'].create({
                        'name': f'Agenda {specialty.name} - {doctor.partner_id.name}',
                        'doctor_id': doctor.id,
                        'specialty_id': specialty.id,
                        'active': True,
                    })
        return doctors
