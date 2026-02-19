# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalDoctorSpecialty(models.Model):
    _name = 'medical.doctor.specialty'
    _description = 'Especialidad del Médico'
    _order = 'sequence, specialty_id'

    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de visualización'
    )
    doctor_id = fields.Many2one(
        'res.partner',
        string='Médico',
        required=True,
        ondelete='cascade',
        domain=[('is_doctor', '=', True)]
    )
    specialty_id = fields.Many2one(
        'medical.specialty',
        string='Especialidad',
        required=True,
        ondelete='restrict'
    )
    duration = fields.Float(
        string='Duración (minutos)',
        required=True,
        default=30.0,
        help='Duración estimada del turno en minutos'
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está inactivo, no se podrán crear turnos para esta especialidad'
    )

    _sql_constraints = [
        ('unique_doctor_specialty', 
         'UNIQUE(doctor_id, specialty_id)', 
         'El médico ya tiene asignada esta especialidad.'),
    ]

    @api.constrains('duration')
    def _check_duration(self):
        """Validar que la duración sea positiva"""
        for record in self:
            if record.duration <= 0:
                raise ValidationError(_('La duración debe ser mayor a 0 minutos.'))
            if record.duration > 480:  # 8 horas
                raise ValidationError(_('La duración no puede ser mayor a 480 minutos (8 horas).'))

    def name_get(self):
        """Mostrar nombre personalizado"""
        result = []
        for record in self:
            name = f"{record.specialty_id.name} ({int(record.duration)} min)"
            result.append((record.id, name))
        return result
