# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, time
import logging

_logger = logging.getLogger(__name__)


class AppointmentSlot(models.Model):
    _name = 'appointment.slot'
    _description = 'Slot de Turno'
    _order = 'date, start_time'
    _rec_name = 'display_name'

    display_name = fields.Char(
        string='Nombre',
        compute='_compute_display_name',
        store=True
    )
    
    # Relaciones
    doctor_id = fields.Many2one(
        'res.partner',
        string='Médico',
        required=True,
        domain=[('is_doctor', '=', True)],
        ondelete='cascade',
        index=True
    )
    specialty_id = fields.Many2one(
        'medical.specialty',
        string='Especialidad',
        required=True,
        index=True
    )
    doctor_specialty_line_id = fields.Many2one(
        'medical.doctor.specialty',
        string='Línea Médico-Especialidad',
        required=True,
        ondelete='cascade',
        index=True
    )
    schedule_id = fields.Many2one(
        'medical.schedule',
        string='Agenda',
        required=True,
        ondelete='cascade',
        index=True
    )
    appointment_id = fields.Many2one(
        'medical.appointment',
        string='Turno',
        ondelete='set null'
    )
    
    # Fecha y hora
    date = fields.Date(
        string='Fecha',
        required=True,
        index=True
    )
    start_time = fields.Float(
        string='Hora Inicio',
        required=True
    )
    end_time = fields.Float(
        string='Hora Fin',
        required=True
    )
    start_time_display = fields.Char(
        string='Inicio (HH:MM)',
        compute='_compute_time_display',
        store=True
    )
    end_time_display = fields.Char(
        string='Fin (HH:MM)',
        compute='_compute_time_display',
        store=True
    )
    duration = fields.Float(
        string='Duración (minutos)',
        compute='_compute_duration',
        store=True
    )
    
    # Datetime combinados para facilitar búsquedas
    start_datetime = fields.Datetime(
        string='Inicio',
        compute='_compute_datetimes',
        store=True,
        index=True
    )
    end_datetime = fields.Datetime(
        string='Fin',
        compute='_compute_datetimes',
        store=True,
        index=True
    )
    
    # Estado
    state = fields.Selection([
        ('available', 'Disponible'),
        ('reserved', 'Reservado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='available', required=True, index=True)
    
    # SQL constraints
    _sql_constraints = [
        ('unique_slot', 
         'UNIQUE(doctor_id, date, start_time)', 
         'Ya existe un slot para este médico en esta fecha y hora.')
    ]

    @api.depends('doctor_id', 'specialty_id', 'date', 'start_time')
    def _compute_display_name(self):
        for record in self:
            if record.doctor_id and record.specialty_id and record.date:
                record.display_name = f"{record.doctor_id.name} - {record.specialty_id.name} - {record.date} {record.start_time_display}"
            else:
                record.display_name = _('Nuevo Slot')

    @api.depends('start_time', 'end_time')
    def _compute_time_display(self):
        for record in self:
            record.start_time_display = '{:02.0f}:{:02.0f}'.format(
                *divmod(record.start_time * 60, 60)
            )
            record.end_time_display = '{:02.0f}:{:02.0f}'.format(
                *divmod(record.end_time * 60, 60)
            )

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            record.duration = (record.end_time - record.start_time) * 60

    @api.depends('date', 'start_time', 'end_time')
    def _compute_datetimes(self):
        for record in self:
            if record.date and record.start_time is not False:
                # Convertir float a time
                start_hour = int(record.start_time)
                start_minute = int((record.start_time - start_hour) * 60)
                start_time_obj = time(start_hour, start_minute)
                
                end_hour = int(record.end_time)
                end_minute = int((record.end_time - end_hour) * 60)
                end_time_obj = time(end_hour, end_minute)
                
                # Combinar con la fecha
                record.start_datetime = datetime.combine(record.date, start_time_obj)
                record.end_datetime = datetime.combine(record.date, end_time_obj)
            else:
                record.start_datetime = False
                record.end_datetime = False

    @api.model
    def generate_slots_for_date_range(self, doctor_id, specialty_id, start_date, end_date):
        """
        Genera slots para un médico y especialidad en un rango de fechas
        """
        if isinstance(start_date, str):
            start_date = fields.Date.from_string(start_date)
        if isinstance(end_date, str):
            end_date = fields.Date.from_string(end_date)
            
        # Buscar la línea médico-especialidad
        doctor_specialty = self.env['medical.doctor.specialty'].search([
            ('doctor_id', '=', doctor_id),
            ('specialty_id', '=', specialty_id),
            ('active', '=', True)
        ], limit=1)
        
        if not doctor_specialty:
            _logger.warning(f"No se encontró relación activa entre médico {doctor_id} y especialidad {specialty_id}")
            return self.env['appointment.slot']
        
        # Buscar la agenda activa
        schedule = self.env['medical.schedule'].search([
            ('doctor_id', '=', doctor_id),
            ('specialty_id', '=', specialty_id),
            ('active', '=', True)
        ], limit=1)
        
        if not schedule:
            _logger.warning(f"No se encontró agenda activa para médico {doctor_id} y especialidad {specialty_id}")
            return self.env['appointment.slot']
        
        if not schedule.schedule_line_ids:
            _logger.warning(f"La agenda {schedule.id} no tiene líneas configuradas")
            return self.env['appointment.slot']
        
        # Duración del turno
        duration = doctor_specialty.duration / 60.0  # Convertir minutos a horas (float)
        
        slots_created = self.env['appointment.slot']
        current_date = start_date
        
        while current_date <= end_date:
            # Obtener el día de la semana (0=Lunes, 6=Domingo)
            weekday = str(current_date.weekday())
            
            # Buscar líneas de agenda para este día
            schedule_lines = schedule.schedule_line_ids.filtered(
                lambda l: l.day_of_week == weekday
            )
            
            for line in schedule_lines:
                # Generar slots para este rango horario
                current_time = line.hour_from
                _logger.info(f"Generando slots para {current_date} - Rango: {line.hour_from} a {line.hour_to} - Duración: {duration}")
                
                while current_time + duration <= line.hour_to:
                    # Verificar si ya existe este slot
                    existing_slot = self.search([
                        ('doctor_id', '=', doctor_id),
                        ('date', '=', current_date),
                        ('start_time', '=', current_time),
                    ], limit=1)
                    
                    if not existing_slot:
                        try:
                            _logger.debug(f"Creando slot: {current_date} de {current_time} a {current_time + duration}")
                            slot = self.create({
                                'doctor_id': doctor_id,
                                'specialty_id': specialty_id,
                                'doctor_specialty_line_id': doctor_specialty.id,
                                'schedule_id': schedule.id,
                                'date': current_date,
                                'start_time': current_time,
                                'end_time': current_time + duration,
                                'state': 'available',
                            })
                            _logger.debug(f"Slot creado: start_time_display={slot.start_time_display}, end_time_display={slot.end_time_display}")
                            slots_created |= slot
                        except Exception as e:
                            _logger.error(f"Error creando slot: {str(e)}")
                    else:
                        slots_created |= existing_slot
                    
                    current_time += duration
            
            current_date += timedelta(days=1)
        
        _logger.info(f"Generados/encontrados {len(slots_created)} slots para médico {doctor_id}, especialidad {specialty_id}")
        return slots_created

    @api.model
    def get_available_slots(self, specialty_id, doctor_id=None, start_date=None, end_date=None):
        """
        Obtiene slots disponibles, generándolos si no existen
        """
        if not start_date:
            start_date = fields.Date.today()
        if not end_date:
            end_date = fields.Date.today() + timedelta(days=30)
            
        if isinstance(start_date, str):
            start_date = fields.Date.from_string(start_date)
        if isinstance(end_date, str):
            end_date = fields.Date.from_string(end_date)
        
        domain = [
            ('specialty_id', '=', specialty_id),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('state', '=', 'available'),
        ]
        
        if doctor_id:
            domain.append(('doctor_id', '=', doctor_id))
            # Generar slots para este médico
            self.generate_slots_for_date_range(doctor_id, specialty_id, start_date, end_date)
        else:
            # Buscar todos los médicos que atienden esta especialidad
            doctor_specialties = self.env['medical.doctor.specialty'].search([
                ('specialty_id', '=', specialty_id),
                ('active', '=', True)
            ])
            
            for ds in doctor_specialties:
                self.generate_slots_for_date_range(ds.doctor_id.id, specialty_id, start_date, end_date)
        
        # Buscar slots disponibles
        available_slots = self.search(domain, order='date, start_time')
        return available_slots

    def action_reserve(self):
        """Reservar slot"""
        self.ensure_one()
        if self.state != 'available':
            raise ValidationError(_('Este slot no está disponible'))
        self.state = 'reserved'

    def action_release(self):
        """Liberar slot"""
        self.ensure_one()
        self.write({
            'state': 'available',
            'appointment_id': False
        })

    def action_cancel(self):
        """Cancelar slot"""
        self.state = 'cancelled'
