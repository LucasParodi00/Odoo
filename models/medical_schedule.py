# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalSchedule(models.Model):
    """
    Agenda del médico - Define la disponibilidad base del profesional.
    """
    _name = 'medical.schedule'
    _description = 'Agenda Médica'
    _order = 'doctor_id, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
        help='Nombre descriptivo de la agenda'
    )
    
    doctor_id = fields.Many2one(
        'medical.doctor',
        string='Médico',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True,
        help='Solo puede haber una agenda activa por médico'
    )
    
    date_start = fields.Date(
        string='Fecha Inicio',
        tracking=True,
        help='Fecha desde la cual aplica esta agenda'
    )
    
    date_end = fields.Date(
        string='Fecha Fin',
        tracking=True,
        help='Fecha hasta la cual aplica esta agenda'
    )
    
    notes = fields.Text(
        string='Notas'
    )
    
    # Líneas de horarios
    schedule_line_ids = fields.One2many(
        'medical.schedule.line',
        'schedule_id',
        string='Horarios de Trabajo',
        help='Definir días y rangos horarios de trabajo'
    )
    
    # Bloqueos
    block_ids = fields.One2many(
        'medical.schedule.block',
        'schedule_id',
        string='Bloqueos',
        help='Vacaciones, ausencias o bloqueos manuales'
    )
    
    @api.constrains('active', 'doctor_id')
    def _check_active_schedule(self):
        """Solo puede haber una agenda activa por médico"""
        for schedule in self:
            if schedule.active:
                other_active = self.search([
                    ('doctor_id', '=', schedule.doctor_id.id),
                    ('active', '=', True),
                    ('id', '!=', schedule.id)
                ])
                if other_active:
                    raise ValidationError(
                        _('El médico %s ya tiene una agenda activa: %s') % 
                        (schedule.doctor_id.name, other_active[0].name)
                    )
    
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for schedule in self:
            if schedule.date_start and schedule.date_end:
                if schedule.date_start > schedule.date_end:
                    raise ValidationError(
                        _('La fecha de inicio no puede ser posterior a la fecha de fin.')
                    )
