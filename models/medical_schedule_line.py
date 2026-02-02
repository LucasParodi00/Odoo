# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalScheduleLine(models.Model):
    """
    Líneas de agenda - Rangos horarios por día de la semana.
    Permite múltiples rangos por día.
    """
    _name = 'medical.schedule.line'
    _description = 'Línea de Agenda Médica'
    _order = 'schedule_id, day_of_week, hour_from'

    schedule_id = fields.Many2one(
        'medical.schedule',
        string='Agenda',
        required=True,
        ondelete='cascade'
    )
    
    day_of_week = fields.Selection([
        ('0', 'Lunes'),
        ('1', 'Martes'),
        ('2', 'Miércoles'),
        ('3', 'Jueves'),
        ('4', 'Viernes'),
        ('5', 'Sábado'),
        ('6', 'Domingo')
    ], string='Día de la Semana', required=True)
    
    hour_from = fields.Float(
        string='Hora Desde',
        required=True,
        help='Hora de inicio en formato 24hs (ej. 8.5 = 08:30)'
    )
    
    hour_to = fields.Float(
        string='Hora Hasta',
        required=True,
        help='Hora de fin en formato 24hs (ej. 17.0 = 17:00)'
    )
    
    # Campos computados para mejor visualización
    hour_from_display = fields.Char(
        string='Desde',
        compute='_compute_hour_display',
        store=True
    )
    
    hour_to_display = fields.Char(
        string='Hasta',
        compute='_compute_hour_display',
        store=True
    )
    
    @api.depends('hour_from', 'hour_to')
    def _compute_hour_display(self):
        for line in self:
            line.hour_from_display = self._float_to_time_str(line.hour_from)
            line.hour_to_display = self._float_to_time_str(line.hour_to)
    
    def _float_to_time_str(self, hour_float):
        """Convierte float a string de hora (ej. 8.5 -> '08:30')"""
        hours = int(hour_float)
        minutes = int((hour_float - hours) * 60)
        return f'{hours:02d}:{minutes:02d}'
    
    @api.constrains('hour_from', 'hour_to')
    def _check_hours(self):
        for line in self:
            if line.hour_from < 0 or line.hour_from >= 24:
                raise ValidationError(_('La hora desde debe estar entre 0 y 23:59.'))
            if line.hour_to < 0 or line.hour_to > 24:
                raise ValidationError(_('La hora hasta debe estar entre 0 y 24:00.'))
            if line.hour_from >= line.hour_to:
                raise ValidationError(_('La hora desde debe ser menor a la hora hasta.'))
    
    @api.constrains('schedule_id', 'day_of_week', 'hour_from', 'hour_to')
    def _check_overlapping(self):
        """Verificar que no haya solapamiento de horarios en el mismo día"""
        for line in self:
            overlapping = self.search([
                ('schedule_id', '=', line.schedule_id.id),
                ('day_of_week', '=', line.day_of_week),
                ('id', '!=', line.id),
                '|',
                '&', ('hour_from', '<=', line.hour_from), ('hour_to', '>', line.hour_from),
                '&', ('hour_from', '<', line.hour_to), ('hour_to', '>=', line.hour_to),
            ])
            if overlapping:
                day_name = dict(self._fields['day_of_week'].selection)[line.day_of_week]
                raise ValidationError(
                    _('Ya existe un horario que se solapa en %s de %s a %s') % 
                    (day_name, line.hour_from_display, line.hour_to_display)
                )
