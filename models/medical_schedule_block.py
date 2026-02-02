# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalScheduleBlock(models.Model):
    """
    Bloqueos de agenda - Vacaciones, ausencias o bloqueos manuales.
    """
    _name = 'medical.schedule.block'
    _description = 'Bloqueo de Agenda'
    _order = 'date_from desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Motivo',
        required=True,
        tracking=True,
        help='Motivo del bloqueo (ej. Vacaciones, Congreso, Ausencia personal)'
    )
    
    schedule_id = fields.Many2one(
        'medical.schedule',
        string='Agenda',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    doctor_id = fields.Many2one(
        'medical.doctor',
        string='Médico',
        related='schedule_id.doctor_id',
        store=True,
        readonly=True
    )
    
    block_type = fields.Selection([
        ('vacation', 'Vacaciones'),
        ('absence', 'Ausencia'),
        ('training', 'Capacitación'),
        ('congress', 'Congreso'),
        ('manual', 'Bloqueo Manual')
    ], string='Tipo de Bloqueo', required=True, default='manual', tracking=True)
    
    date_from = fields.Datetime(
        string='Fecha/Hora Desde',
        required=True,
        tracking=True
    )
    
    date_to = fields.Datetime(
        string='Fecha/Hora Hasta',
        required=True,
        tracking=True
    )
    
    all_day = fields.Boolean(
        string='Todo el Día',
        default=False,
        help='Si está marcado, el bloqueo aplica todo el día'
    )
    
    notes = fields.Text(
        string='Notas'
    )
    
    color = fields.Integer(
        string='Color',
        default=1
    )
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for block in self:
            if block.date_from >= block.date_to:
                raise ValidationError(
                    _('La fecha/hora de inicio debe ser anterior a la fecha/hora de fin.')
                )
    
    @api.constrains('schedule_id', 'date_from', 'date_to')
    def _check_overlapping(self):
        """Verificar que no haya bloqueos solapados"""
        for block in self:
            overlapping = self.search([
                ('schedule_id', '=', block.schedule_id.id),
                ('id', '!=', block.id),
                ('date_from', '<', block.date_to),
                ('date_to', '>', block.date_from),
            ])
            if overlapping:
                raise ValidationError(
                    _('Ya existe un bloqueo que se solapa con este período: %s') % 
                    overlapping[0].name
                )
