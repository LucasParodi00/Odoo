# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalSchedule(models.Model):
    _name = 'medical.schedule'
    _description = 'Agenda Médica'
    _order = 'name'

    name = fields.Char(
        string='Nombre de la Agenda',
        required=True,
        help='Nombre descriptivo de la agenda'
    )
    doctor_id = fields.Many2one(
        'res.partner',
        string='Médico',
        required=True,
        domain=[('is_doctor', '=', True)],
        ondelete='cascade',
        help='Médico al que pertenece la agenda'
    )
    specialty_id = fields.Many2one(
        'medical.specialty',
        string='Especialidad',
        required=True,
        help='Especialidad médica asociada a esta agenda'
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está inactivo, la agenda no se usará para generar turnos'
    )
    schedule_line_ids = fields.One2many(
        'medical.schedule.line',
        'schedule_id',
        string='Horarios',
        help='Líneas de horario de la agenda'
    )
    
    _sql_constraints = [
        ('unique_doctor_specialty_name', 
         'UNIQUE(doctor_id, specialty_id, name)', 
         'Ya existe una agenda con ese nombre para este médico y especialidad.'),
    ]

    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        """Limpiar la especialidad si no pertenece al médico seleccionado"""
        result = {}
        if self.doctor_id:
            # Obtener especialidades activas del médico
            active_specialty_ids = self.doctor_id.doctor_specialty_ids.ids
            
            # Limpiar la especialidad si no pertenece al médico
            if self.specialty_id and self.specialty_id.id not in active_specialty_ids:
                self.specialty_id = False
            
            # Actualizar dominio para mostrar solo especialidades activas del médico
            result['domain'] = {
                'specialty_id': [('id', 'in', active_specialty_ids)]
            }
        else:
            # Si no hay médico, limpiar especialidad y sin restricciones
            self.specialty_id = False
            result['domain'] = {'specialty_id': []}
        
        return result

    @api.constrains('specialty_id', 'doctor_id')
    def _check_specialty_belongs_to_doctor(self):
        """Validar que la especialidad pertenezca al médico y esté activa"""
        for record in self:
            if record.specialty_id not in record.doctor_id.doctor_specialty_ids:
                raise ValidationError(
                    _('La especialidad %s no está asignada al médico %s o no está activa.') %
                    (record.specialty_id.name, record.doctor_id.name)
                )


class MedicalScheduleLine(models.Model):
    _name = 'medical.schedule.line'
    _description = 'Línea de Horario de Agenda'
    _order = 'day_of_week, hour_from'

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
        ('6', 'Domingo'),
    ], string='Día de la Semana', required=True)
    hour_from = fields.Float(
        string='Hora Desde',
        required=True,
        help='Hora de inicio en formato 24h (ej: 8.0 = 08:00, 13.5 = 13:30)'
    )
    hour_to = fields.Float(
        string='Hora Hasta',
        required=True,
        help='Hora de fin en formato 24h (ej: 13.0 = 13:00, 20.5 = 20:30)'
    )
    
    # Campos computados para mostrar mejor las horas
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
        """Convertir horas float a formato HH:MM"""
        for record in self:
            record.hour_from_display = self._float_to_time(record.hour_from)
            record.hour_to_display = self._float_to_time(record.hour_to)

    def _float_to_time(self, hour_float):
        """Convertir float a string HH:MM"""
        if hour_float is False:
            return ''
        hours = int(hour_float)
        minutes = int((hour_float - hours) * 60)
        return '%02d:%02d' % (hours, minutes)

    @api.constrains('hour_from', 'hour_to')
    def _check_hours(self):
        """Validar que las horas sean correctas"""
        for record in self:
            if record.hour_from < 0 or record.hour_from >= 24:
                raise ValidationError(_('La hora de inicio debe estar entre 00:00 y 23:59'))
            if record.hour_to < 0 or record.hour_to > 24:
                raise ValidationError(_('La hora de fin debe estar entre 00:00 y 24:00'))
            if record.hour_from >= record.hour_to:
                raise ValidationError(_('La hora de inicio debe ser menor que la hora de fin'))

    @api.constrains('schedule_id', 'day_of_week', 'hour_from', 'hour_to')
    def _check_overlap(self):
        """Validar que no haya solapamiento de horarios en el mismo día para la misma agenda"""
        for record in self:
            if not record.schedule_id:
                continue
                
            # Buscar horarios que se solapen en el mismo día y agenda
            overlapping = self.search([
                ('id', '!=', record.id),
                ('schedule_id', '=', record.schedule_id.id),
                ('day_of_week', '=', record.day_of_week),
            ])
            
            # Verificar solapamiento manual
            for line in overlapping:
                # Hay solapamiento si:
                # - El inicio del nuevo horario está dentro de un horario existente
                # - El fin del nuevo horario está dentro de un horario existente
                # - El nuevo horario contiene completamente un horario existente
                if (line.hour_from < record.hour_to and line.hour_to > record.hour_from):
                    day_name = dict(self._fields['day_of_week'].selection).get(record.day_of_week)
                    raise ValidationError(
                        _('Ya existe un horario que se solapa en %s.\n'
                          'Horario existente: %s a %s\n'
                          'Horario nuevo: %s a %s') %
                        (day_name, 
                         line.hour_from_display, line.hour_to_display,
                         record.hour_from_display, record.hour_to_display)
                    )
