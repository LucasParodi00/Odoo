# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class MedicalAppointment(models.Model):
    _name = 'medical.appointment'
    _description = 'Turno Médico'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'appointment_date desc, appointment_time'
    _rec_name = 'display_name'

    name = fields.Char(
        string='Número de Turno',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('Nuevo')
    )
    display_name = fields.Char(
        string='Nombre',
        compute='_compute_display_name',
        store=True
    )

    # Slot
    slot_id = fields.Many2one(
        'appointment.slot',
        string='Slot',
        required=True,
        ondelete='restrict',
        tracking=True,
        help='Slot de horario reservado para este turno'
    )

    # Datos del turno (copiados del slot)
    doctor_id = fields.Many2one(
        'res.partner',
        string='Médico',
        domain=[('is_doctor', '=', True)],
        tracking=True,
        related='slot_id.doctor_id',
        store=True,
        readonly=True
    )
    specialty_id = fields.Many2one(
        'medical.specialty',
        string='Especialidad',
        tracking=True,
        related='slot_id.specialty_id',
        store=True,
        readonly=True
    )
    doctor_specialty_line_id = fields.Many2one(
        'medical.doctor.specialty',
        string='Línea Médico-Especialidad',
        related='slot_id.doctor_specialty_line_id',
        store=True,
        readonly=True
    )
    duration = fields.Float(
        string='Duración (min)',
        related='doctor_specialty_line_id.duration',
        readonly=True
    )
    
    # Fecha y hora
    appointment_date = fields.Date(
        string='Fecha',
        tracking=True,
        related='slot_id.date',
        store=True,
        readonly=True
    )
    appointment_time = fields.Float(
        string='Hora',
        related='slot_id.start_time',
        store=True,
        readonly=True
    )
    appointment_time_display = fields.Char(
        string='Hora de Turno',
        compute='_compute_appointment_time_display',
        store=True
    )
    appointment_datetime = fields.Datetime(
        string='Fecha y Hora',
        compute='_compute_appointment_datetime',
        store=True,
        index=True
    )
    appointment_end_datetime = fields.Datetime(
        string='Fecha y Hora Fin',
        compute='_compute_appointment_datetime',
        store=True
    )

    # Paciente
    patient_type = fields.Selection([
        ('human', 'Humano'),
        ('pet', 'Mascota')
    ], string='Tipo de Paciente', default='human', required=True, tracking=True)
    
    patient_id = fields.Many2one(
        'res.partner',
        string='Paciente Humano',
        domain=[('is_patient', '=', True)],
        tracking=True
    )
    pet_id = fields.Many2one(
        'medical.patient.pet',
        string='Mascota',
        tracking=True
    )
    patient_display = fields.Char(
        string='Paciente',
        compute='_compute_patient_display',
        store=True
    )

    # Estado
    state = fields.Selection([
        ('scheduled', 'Agendado'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'En Curso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
        ('no_show', 'No Asistió')
    ], string='Estado', default='scheduled', required=True, tracking=True, index=True)

    # Pago
    payment_state = fields.Selection([
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('refunded', 'Reembolsado')
    ], string='Estado de Pago', default='pending', tracking=True)

    # Notas
    notes = fields.Text(string='Notas')

    @api.depends('name', 'patient_display', 'appointment_date')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.name != _('Nuevo'):
                record.display_name = f"{record.name} - {record.patient_display or 'Sin paciente'}"
            else:
                record.display_name = _('Nuevo Turno')

    @api.depends('patient_type', 'patient_id', 'pet_id')
    def _compute_patient_display(self):
        for record in self:
            if record.patient_type == 'human' and record.patient_id:
                record.patient_display = record.patient_id.name
            elif record.patient_type == 'pet' and record.pet_id:
                record.patient_display = f"{record.pet_id.name} ({record.pet_id.owner_id.name})"
            else:
                record.patient_display = ''

    @api.depends('appointment_time')
    def _compute_appointment_time_display(self):
        for record in self:
            if record.appointment_time is not False:
                hours = int(record.appointment_time)
                minutes = int((record.appointment_time - hours) * 60)
                record.appointment_time_display = '{:02d}:{:02d}'.format(hours, minutes)
            else:
                record.appointment_time_display = ''

    @api.depends('appointment_date', 'appointment_time', 'duration')
    def _compute_appointment_datetime(self):
        for record in self:
            if record.appointment_date and record.appointment_time is not False:
                hours = int(record.appointment_time)
                minutes = int((record.appointment_time - hours) * 60)
                record.appointment_datetime = datetime.combine(
                    record.appointment_date,
                    datetime.min.time()
                ).replace(hour=hours, minute=minutes)
                
                if record.duration:
                    record.appointment_end_datetime = record.appointment_datetime + timedelta(minutes=record.duration)
                else:
                    record.appointment_end_datetime = record.appointment_datetime
            else:
                record.appointment_datetime = False
                record.appointment_end_datetime = False

    @api.constrains('patient_type', 'patient_id', 'pet_id')
    def _check_patient(self):
        for record in self:
            if record.patient_type == 'human' and not record.patient_id:
                raise ValidationError(_('Debe seleccionar un paciente humano'))
            if record.patient_type == 'pet' and not record.pet_id:
                raise ValidationError(_('Debe seleccionar una mascota'))

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("=== Iniciando creación de turno(s) ===")
        for vals in vals_list:
            _logger.info(f"Valores recibidos: {vals}")
            
            # Generar número de turno
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or _('Nuevo')
                _logger.info(f"Número de turno generado: {vals['name']}")
            
            # Reservar el slot
            if vals.get('slot_id'):
                slot = self.env['appointment.slot'].browse(vals['slot_id'])
                _logger.info(f"Slot seleccionado: ID={slot.id}, Estado={slot.state}, Fecha={slot.date}, Hora={slot.start_time_display}")
                
                if slot.state != 'available':
                    raise ValidationError(_('El slot seleccionado no está disponible'))
                
                slot.action_reserve()
                _logger.info(f"Slot reservado exitosamente. Nuevo estado: {slot.state}")
        
        _logger.info("Llamando a super().create()")
        appointments = super(MedicalAppointment, self).create(vals_list)
        _logger.info(f"Turnos creados: {len(appointments)}")
        
        # Actualizar la referencia del turno en el slot
        for appointment in appointments:
            _logger.info(f"Turno creado: ID={appointment.id}, Nombre={appointment.name}, Paciente={appointment.patient_display}")
            appointment.slot_id.write({'appointment_id': appointment.id})
            _logger.info(f"Referencia actualizada en slot {appointment.slot_id.id}")
        
        _logger.info("=== Creación de turno(s) completada ===")
        return appointments

    def write(self, vals):
        # Si se cancela el turno, liberar el slot
        if 'state' in vals and vals['state'] in ['cancelled', 'no_show']:
            for record in self:
                if record.slot_id:
                    record.slot_id.action_release()
        
        return super(MedicalAppointment, self).write(vals)

    def unlink(self):
        """Liberar slot al eliminar turno"""
        for record in self:
            if record.slot_id and record.slot_id.state == 'reserved':
                record.slot_id.action_release()
        return super(MedicalAppointment, self).unlink()

    def action_confirm(self):
        """Confirmar turno"""
        for record in self:
            record.state = 'confirmed'

    def action_start(self):
        """Iniciar consulta"""
        for record in self:
            record.state = 'in_progress'

    def action_complete(self):
        """Completar turno"""
        for record in self:
            record.state = 'completed'

    def action_cancel(self):
        """Cancelar turno"""
        for record in self:
            record.state = 'cancelled'

    def action_mark_no_show(self):
        """Marcar como no asistió"""
        for record in self:
            record.state = 'no_show'
