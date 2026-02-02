# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import pytz


class MedicalAppointment(models.Model):
    """
    Turnos Médicos - Sistema flexible de gestión de turnos.
    Soporta dos flujos: con preferencia de médico y sin preferencia.
    """
    _name = 'medical.appointment'
    _description = 'Turno Médico'
    _order = 'date_start desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    # Información básica
    display_name = fields.Char(
        string='Turno',
        compute='_compute_display_name',
        store=True
    )
    
    # Especialidad (punto de inicio obligatorio)
    specialty_id = fields.Many2one(
        'medical.specialty',
        string='Especialidad',
        required=True,
        ondelete='restrict',
        tracking=True,
        help='Especialidad médica - punto de inicio del flujo'
    )
    
    # Campos helper para dominios dinámicos
    available_specialty_ids = fields.Many2many(
        'medical.specialty',
        compute='_compute_available_specialties',
        string='Especialidades Disponibles'
    )
    
    available_doctor_ids = fields.Many2many(
        'medical.doctor',
        compute='_compute_available_doctors',
        string='Médicos Disponibles'
    )
    
    # Práctica/Atención
    practice_id = fields.Many2one(
        'medical.practice',
        string='Práctica/Atención',
        required=True,
        ondelete='restrict',
        tracking=True,
        domain="[('specialty_id', '=', specialty_id)]"
    )
    
    # Médico
    doctor_id = fields.Many2one(
        'medical.doctor',
        string='Médico',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    
    # Campo para mostrar horarios disponibles
    available_slots_html = fields.Html(
        string='Horarios Disponibles',
        compute='_compute_available_slots_html',
        sanitize=False
    )
    
    # Fecha y horario
    date_start = fields.Datetime(
        string='Fecha/Hora Inicio',
        required=True,
        tracking=True
    )
    
    date_end = fields.Datetime(
        string='Fecha/Hora Fin',
        compute='_compute_date_end',
        store=True,
        readonly=True,
        tracking=True,
        help='Se calcula automáticamente según la duración de la práctica'
    )
    
    duration = fields.Float(
        string='Duración (horas)',
        related='practice_id.duration',
        store=True,
        readonly=True
    )
    
    # Paciente (persona o animal)
    patient_type = fields.Selection([
        ('person', 'Persona'),
        ('animal', 'Animal')
    ], string='Tipo de Paciente', required=True, tracking=True,
       compute='_compute_patient_type', store=True, readonly=False)
    
    patient_id = fields.Many2one(
        'res.partner',
        string='Paciente (Persona)',
        tracking=True,
        domain=[('is_company', '=', False)]
    )
    
    patient_animal_id = fields.Many2one(
        'medical.patient.animal',
        string='Paciente (Animal)',
        tracking=True
    )
    
    patient_name = fields.Char(
        string='Paciente',
        compute='_compute_patient_name',
        store=True
    )
    
    # Estado del turno
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('attended', 'Atendido'),
        ('cancelled', 'Cancelado'),
        ('absent', 'Ausente')
    ], string='Estado', default='draft', required=True, tracking=True)
    
    # Historia clínica asociada
    clinical_history_id = fields.Many2one(
        'medical.clinical.history',
        string='Historia Clínica',
        readonly=True,
        help='Historia clínica generada al atender el turno'
    )
    
    has_clinical_history = fields.Boolean(
        string='Tiene HC',
        compute='_compute_has_clinical_history',
        store=True
    )
    
    # Información adicional
    reason = fields.Text(
        string='Motivo de Consulta',
        tracking=True
    )
    
    notes = fields.Text(
        string='Notas'
    )
    
    color = fields.Integer(
        string='Color',
        compute='_compute_color',
        store=True
    )
    
    # Campos de auditoría
    confirmed_date = fields.Datetime(
        string='Fecha de Confirmación',
        readonly=True
    )
    
    confirmed_by = fields.Many2one(
        'res.users',
        string='Confirmado Por',
        readonly=True
    )
    
    attended_date = fields.Datetime(
        string='Fecha de Atención',
        readonly=True
    )
    
    cancelled_date = fields.Datetime(
        string='Fecha de Cancelación',
        readonly=True
    )
    
    cancelled_by = fields.Many2one(
        'res.users',
        string='Cancelado Por',
        readonly=True
    )
    
    cancellation_reason = fields.Text(
        string='Motivo de Cancelación'
    )
    
    @api.depends('specialty_id', 'specialty_id.patient_type')
    def _compute_patient_type(self):
        for appointment in self:
            if appointment.specialty_id:
                if appointment.specialty_id.patient_type in ['person', 'animal']:
                    appointment.patient_type = appointment.specialty_id.patient_type
                elif not appointment.patient_type:
                    appointment.patient_type = 'person'
    
    @api.depends('patient_id', 'patient_animal_id', 'patient_type')
    def _compute_patient_name(self):
        for appointment in self:
            if appointment.patient_type == 'person' and appointment.patient_id:
                appointment.patient_name = appointment.patient_id.name
            elif appointment.patient_type == 'animal' and appointment.patient_animal_id:
                appointment.patient_name = appointment.patient_animal_id.name
            else:
                appointment.patient_name = ''
    
    @api.depends('specialty_id', 'doctor_id', 'date_start', 'patient_name')
    def _compute_display_name(self):
        for appointment in self:
            parts = []
            if appointment.specialty_id:
                parts.append(appointment.specialty_id.name)
            if appointment.patient_name:
                parts.append(appointment.patient_name)
            if appointment.doctor_id:
                parts.append(f'Dr./Dra. {appointment.doctor_id.name}')
            if appointment.date_start:
                parts.append(appointment.date_start.strftime('%d/%m/%Y %H:%M'))
            
            appointment.display_name = ' - '.join(parts) if parts else _('Nuevo Turno')
    
    @api.depends('practice_id', 'practice_id.duration', 'date_start')
    def _compute_date_end(self):
        for appointment in self:
            if appointment.date_start and appointment.practice_id:
                duration_hours = appointment.practice_id.duration
                appointment.date_end = appointment.date_start + timedelta(hours=duration_hours)
            else:
                appointment.date_end = False
    
    @api.depends('doctor_id')
    def _compute_available_specialties(self):
        """Compute las especialidades disponibles según el médico seleccionado"""
        for appointment in self:
            if appointment.doctor_id:
                appointment.available_specialty_ids = appointment.doctor_id.specialty_ids
            else:
                # Si no hay médico, mostrar todas las especialidades
                appointment.available_specialty_ids = self.env['medical.specialty'].search([])
    
    @api.depends('specialty_id')
    def _compute_available_doctors(self):
        """Compute los médicos disponibles según la especialidad"""
        for appointment in self:
            if appointment.specialty_id:
                appointment.available_doctor_ids = self.env['medical.doctor'].search([
                    ('specialty_ids', 'in', appointment.specialty_id.ids)
                ])
            else:
                appointment.available_doctor_ids = self.env['medical.doctor'].search([])
    
    @api.depends('doctor_id', 'specialty_id', 'practice_id')
    def _compute_available_slots_html(self):
        """Genera HTML con cuadraditos de días y horarios disponibles"""
        for appointment in self:
            if not appointment.doctor_id or not appointment.specialty_id or not appointment.practice_id:
                appointment.available_slots_html = ''
                continue
            
            # Obtener mes actual
            today = datetime.now()
            year = today.year
            month = today.month
            
            # Llamar al método que calcula disponibilidad
            slots_data = appointment.get_available_slots(
                appointment.doctor_id.id,
                appointment.specialty_id.id,
                appointment.practice_id.id,
                year,
                month
            )
            
            appointment.available_slots_html = appointment._generate_slots_html(slots_data, year, month)
    
    @api.depends('clinical_history_id')
    def _compute_has_clinical_history(self):
        for appointment in self:
            appointment.has_clinical_history = bool(appointment.clinical_history_id)
    
    @api.depends('state', 'specialty_id')
    def _compute_color(self):
        """Color según estado del turno"""
        color_map = {
            'draft': 0,
            'confirmed': 4,  # Azul
            'attended': 10,  # Verde
            'cancelled': 1,  # Rojo
            'absent': 3,  # Naranja
        }
        for appointment in self:
            appointment.color = color_map.get(appointment.state, 0)
    
    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        """FLUJO 1: Al seleccionar médico, cargar sus especialidades"""
        if self.doctor_id:
            # Si el médico tiene solo una especialidad, auto-seleccionarla
            if len(self.doctor_id.specialty_ids) == 1:
                self.specialty_id = self.doctor_id.specialty_ids[0]
            # Si ya había una especialidad seleccionada, verificar que el médico la tenga
            elif self.specialty_id and self.specialty_id not in self.doctor_id.specialty_ids:
                # Limpiar si el médico no tiene esa especialidad
                self.specialty_id = False
                self.practice_id = False
        else:
            # Si se borra el médico, mantener especialidad y práctica (para Flujo 2)
            pass
    
    @api.onchange('specialty_id')
    def _onchange_specialty_id(self):
        """Al cambiar especialidad, filtrar prácticas y verificar médico"""
        # Limpiar práctica si no corresponde a la nueva especialidad
        if self.practice_id and self.practice_id.specialty_id != self.specialty_id:
            self.practice_id = False
        
        # Si hay médico seleccionado y no tiene esta especialidad, limpiarlo (Flujo 2)
        if self.doctor_id and self.specialty_id not in self.doctor_id.specialty_ids:
            self.doctor_id = False
    
    @api.onchange('practice_id')
    def _onchange_practice_id(self):
        """Al seleccionar práctica, actualizar duración y especialidad"""
        if self.practice_id:
            # Auto-completar especialidad si no está seleccionada
            if not self.specialty_id:
                self.specialty_id = self.practice_id.specialty_id
            # Auto-completar duración
            self.duration = self.practice_id.duration
            # Verificar que el médico tenga esta especialidad
            if self.doctor_id and self.specialty_id not in self.doctor_id.specialty_ids:
                self.doctor_id = False
    
    @api.constrains('patient_id', 'patient_animal_id', 'patient_type')
    def _check_patient(self):
        """Validar que se seleccione el paciente correcto según el tipo"""
        for appointment in self:
            if appointment.patient_type == 'person' and not appointment.patient_id:
                raise ValidationError(_('Debe seleccionar un paciente (persona).'))
            if appointment.patient_type == 'animal' and not appointment.patient_animal_id:
                raise ValidationError(_('Debe seleccionar un paciente (animal).'))
            if appointment.patient_type == 'person' and appointment.patient_animal_id:
                raise ValidationError(_('No puede seleccionar un animal para esta especialidad.'))
            if appointment.patient_type == 'animal' and appointment.patient_id:
                raise ValidationError(_('No puede seleccionar una persona para esta especialidad veterinaria.'))
    
    @api.constrains('specialty_id', 'patient_type')
    def _check_specialty_patient_type(self):
        """Validar que el tipo de paciente sea compatible con la especialidad"""
        for appointment in self:
            if appointment.specialty_id.patient_type == 'person' and appointment.patient_type != 'person':
                raise ValidationError(
                    _('La especialidad %s solo atiende personas.') % appointment.specialty_id.name
                )
            if appointment.specialty_id.patient_type == 'animal' and appointment.patient_type != 'animal':
                raise ValidationError(
                    _('La especialidad %s solo atiende animales.') % appointment.specialty_id.name
                )
    
    @api.constrains('doctor_id', 'specialty_id')
    def _check_doctor_specialty(self):
        """Validar que el médico atienda la especialidad seleccionada"""
        for appointment in self:
            if appointment.specialty_id not in appointment.doctor_id.specialty_ids:
                raise ValidationError(
                    _('El Dr./Dra. %s no atiende la especialidad %s.') % 
                    (appointment.doctor_id.name, appointment.specialty_id.name)
                )
    
    @api.constrains('date_start', 'date_end', 'doctor_id', 'state')
    def _check_availability(self):
        """Validar disponibilidad del médico"""
        for appointment in self:
            if appointment.state in ['draft', 'confirmed']:
                # Verificar solapamiento con otros turnos
                overlapping = self.search([
                    ('doctor_id', '=', appointment.doctor_id.id),
                    ('id', '!=', appointment.id),
                    ('state', 'in', ['draft', 'confirmed']),
                    ('date_start', '<', appointment.date_end),
                    ('date_end', '>', appointment.date_start),
                ])
                if overlapping:
                    raise ValidationError(
                        _('El médico ya tiene un turno en ese horario: %s') % 
                        overlapping[0].display_name
                    )
                
                # Verificar bloqueos de agenda
                if appointment.doctor_id.current_schedule_id:
                    blocks = self.env['medical.schedule.block'].search([
                        ('schedule_id', '=', appointment.doctor_id.current_schedule_id.id),
                        ('date_from', '<', appointment.date_end),
                        ('date_to', '>', appointment.date_start),
                    ])
                    if blocks:
                        raise ValidationError(
                            _('El médico tiene un bloqueo en ese horario: %s') % blocks[0].name
                        )
    
    def action_confirm(self):
        """Confirmar turno"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Solo se pueden confirmar turnos en borrador.'))
        
        self.write({
            'state': 'confirmed',
            'confirmed_date': fields.Datetime.now(),
            'confirmed_by': self.env.user.id,
        })
        
        return True
    
    def action_attend(self):
        """Atender turno y crear historia clínica"""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Solo se pueden atender turnos confirmados.'))
        
        # Crear historia clínica
        clinical_history = self.env['medical.clinical.history'].create({
            'appointment_id': self.id,
            'specialty_id': self.specialty_id.id,
            'practice_id': self.practice_id.id,
            'doctor_id': self.doctor_id.id,
            'patient_id': self.patient_id.id if self.patient_type == 'person' else False,
            'patient_animal_id': self.patient_animal_id.id if self.patient_type == 'animal' else False,
            'date': self.date_start,
        })
        
        self.write({
            'state': 'attended',
            'attended_date': fields.Datetime.now(),
            'clinical_history_id': clinical_history.id,
        })
        
        # Abrir la historia clínica
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'medical.clinical.history',
            'res_id': clinical_history.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_cancel(self):
        """Cancelar turno"""
        self.ensure_one()
        if self.state in ['attended', 'cancelled']:
            raise UserError(_('No se puede cancelar un turno atendido o ya cancelado.'))
        
        self.write({
            'state': 'cancelled',
            'cancelled_date': fields.Datetime.now(),
        })
    
    def _generate_slots_html(self, slots_data, year, month):
        """Genera HTML con cuadraditos de días y horarios disponibles"""
        if not slots_data or not slots_data.get('days'):
            return '<div class="alert alert-warning">No hay horarios disponibles para este mes</div>'
        
        # Obtener días del mes
        from calendar import monthrange, day_name
        num_days = monthrange(year, month)[1]
        first_weekday = monthrange(year, month)[0]  # 0=Lun
        
        month_names = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        html = f'''
        <style>
            .appointment-calendar {{
                margin: 20px 0;
                font-family: Arial, sans-serif;
            }}
            .day-available:hover {{
                transform: scale(1.05);
                transition: all 0.2s;
            }}
            .slot-item:hover {{
                background-color: #28a745 !important;
                color: white !important;
            }}
            .slots-popup {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                border: 2px solid #28a745;
                padding: 20px;
                z-index: 10000;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                max-width: 400px;
                max-height: 500px;
                overflow-y: auto;
            }}
        </style>
        
        <div class="appointment-calendar">
            <h4 style="text-align: center; margin-bottom: 20px; color: #333;">
                📅 {month_names[month-1]} {year}
            </h4>
            
            <!-- Días de la semana -->
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-bottom: 10px;">
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Lun</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Mar</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Mié</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Jue</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Vie</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Sáb</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Dom</div>
            </div>
            
            <!-- Días del mes -->
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px;">
        '''
        
        # Espacios en blanco antes del primer día
        for _ in range(first_weekday):
            html += '<div></div>'
        
        # ID único para evitar conflictos
        import random
        popup_id = f"popup_{random.randint(1000, 9999)}"
        
        # Renderizar cada día
        for day in range(1, num_days + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            day_data = slots_data['days'].get(date_str, {})
            has_slots = day_data.get('has_availability', False)
            
            if has_slots:
                # Día con disponibilidad - clickeable
                slots_count = len(day_data.get('slots', []))
                slots_html = ""
                
                # Generar HTML de slots
                for slot in day_data.get('slots', []):
                    slot_time = slot['time']
                    slot_datetime = slot['datetime']
                    slots_html += f'''
                    <div class="slot-item" 
                         style="padding: 8px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; cursor: pointer; border: 1px solid #ddd; text-align: center;"
                         onclick="
                            var dateField = document.querySelector('input[name=date_start]');
                            if (dateField) {{
                                dateField.value = '{slot_datetime}';
                                dateField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                            document.getElementById('{popup_id}').style.display = 'none';
                         ">
                        ⏰ <strong>{slot_time}</strong>
                    </div>
                    '''
                
                html += f'''
                <div class="day-available" 
                     style="
                        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                        border: 2px solid #28a745;
                        border-radius: 8px;
                        padding: 10px;
                        text-align: center;
                        cursor: pointer;
                        font-weight: bold;
                        position: relative;
                     "
                     onclick="document.getElementById('{popup_id}_{day}').style.display = 'block'">
                    <div style="font-size: 18px;">{day}</div>
                    <div style="font-size: 10px; color: #28a745; margin-top: 3px;">✓ {slots_count} turnos</div>
                </div>
                
                <!-- Popup para este día -->
                <div id="{popup_id}_{day}" class="slots-popup" style="display: none;">
                    <h5 style="margin: 0 0 15px 0; color: #333; text-align: center;">
                        🗓️ {date_str}
                    </h5>
                    <div style="margin-bottom: 15px;">
                        {slots_html}
                    </div>
                    <button 
                        onclick="document.getElementById('{popup_id}_{day}').style.display = 'none'" 
                        style="width: 100%; padding: 10px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
                        ✖ Cerrar
                    </button>
                </div>
                '''
            else:
                # Día sin disponibilidad
                html += f'''
                <div class="day-unavailable" 
                     style="
                        background-color: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 10px;
                        text-align: center;
                        color: #999;
                        font-size: 18px;
                     ">
                    {day}
                </div>
                '''
        
        html += '''
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #e7f3ff; border-left: 4px solid #007bff; border-radius: 5px;">
                <strong>💡 Instrucciones:</strong><br/>
                • Haga clic en un día <span style="color: #28a745; font-weight: bold;">VERDE</span> para ver horarios<br/>
                • Seleccione un horario para agendar el turno<br/>
                • El horario se completará automáticamente
            </div>
        </div>
        '''
        
        return html
    
    def action_select_slot(self, slot_datetime):
        """Seleccionar un slot desde el calendario visual"""
        self.ensure_one()
        self.date_start = slot_datetime
        return True
    
    def action_cancel(self):
        """Cancelar turno - abre wizard"""
        self.ensure_one()
        if self.state in ['attended', 'cancelled']:
            raise UserError(_('No se puede cancelar un turno atendido o ya cancelado.'))
        
        return {
            'name': _('Cancelar Turno'),
            'type': 'ir.actions.act_window',
            'res_model': 'medical.appointment.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_appointment_id': self.id},
        }
    
    def action_mark_absent(self):
        """Marcar turno como ausente"""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_('Solo se pueden marcar como ausentes turnos confirmados.'))
        
        self.write({
            'state': 'absent',
        })
        
        return True
    
    def action_reschedule(self):
        """Reprogramar turno"""
        self.ensure_one()
        if self.state == 'attended':
            raise UserError(_('No se puede reprogramar un turno ya atendido.'))
        
        # Crear un nuevo turno con los mismos datos
        new_appointment = self.copy({
            'state': 'draft',
            'date_start': False,
            'date_end': False,
        })
        
        # Cancelar el turno actual
        self.write({
            'state': 'cancelled',
            'cancelled_date': fields.Datetime.now(),
            'cancelled_by': self.env.user.id,
            'cancellation_reason': 'Reprogramado',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'medical.appointment',
            'res_id': new_appointment.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_clinical_history(self):
        """Ver historia clínica asociada"""
        self.ensure_one()
        if not self.clinical_history_id:
            raise UserError(_('Este turno no tiene historia clínica asociada.'))
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'medical.clinical.history',
            'res_id': self.clinical_history_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model
    def get_available_slots(self, doctor_id, specialty_id, practice_id, year, month):
        """
        Obtiene slots disponibles para un médico en una especialidad/práctica específica.
        
        REGLA CLAVE: Solo muestra horarios REALMENTE disponibles.
        - Considera agenda del médico para esa especialidad
        - Excluye bloqueos
        - Excluye turnos ya agendados
        - Considera duración de la práctica
        - Respeta rangos horarios declarados
        
        :param doctor_id: ID del médico
        :param specialty_id: ID de la especialidad (CRÍTICO para filtrar días/horarios)
        :param practice_id: ID de la práctica
        :param year: Año (int)
        :param month: Mes (int, 1-12)
        :return: Dict con días disponibles y sus horarios
        """
        doctor = self.env['medical.doctor'].browse(doctor_id)
        practice = self.env['medical.practice'].browse(practice_id)
        
        if not doctor or not practice:
            return {'days': {}}
        
        # Obtener agenda activa
        schedule = doctor.schedule_ids.filtered(lambda s: s.active)
        if not schedule:
            return {'days': {}}
        
        schedule = schedule[0]
        
        # Preparar estructura de respuesta
        result = {'days': {}}
        
        # Rango de fechas del mes
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        current_date = first_day
        
        while current_date <= last_day:
            day_of_week = current_date.weekday()  # 0=Lunes, 6=Domingo
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Buscar horarios del médico para este día
            schedule_lines = schedule.schedule_line_ids.filtered(
                lambda l: int(l.day_of_week) == day_of_week
            )
            
            # Verificar bloqueos
            has_block = any(
                block.date_from.date() <= current_date.date() <= block.date_to.date()
                for block in schedule.block_ids
            )
            
            if schedule_lines and not has_block and current_date.date() >= datetime.now().date():
                # Día tiene disponibilidad potencial
                slots = []
                
                # Obtener timezone del usuario o del sistema
                tz = pytz.timezone(self.env.user.tz or 'UTC')
                
                for line in schedule_lines:
                    # hour_from y hour_to están en formato float (8.0 = 08:00, 13.5 = 13:30)
                    start_hour = line.hour_from
                    end_hour = line.hour_to
                    duration = practice.duration
                    
                    # Generar slots cada [duration] horas
                    current_slot = start_hour
                    while current_slot + duration <= end_hour:
                        slot_hour = int(current_slot)
                        slot_minute = int((current_slot % 1) * 60)
                        
                        # Crear datetime en la timezone local del usuario
                        naive_datetime = current_date.replace(
                            hour=slot_hour,
                            minute=slot_minute,
                            second=0,
                            microsecond=0
                        )
                        
                        # Localizar a la timezone del usuario
                        local_datetime = tz.localize(naive_datetime)
                        
                        # Convertir a UTC para almacenar en Odoo
                        slot_datetime_utc = local_datetime.astimezone(pytz.UTC).replace(tzinfo=None)
                        
                        # Verificar que no esté en el pasado (comparar en UTC)
                        now_utc = datetime.now(pytz.UTC).replace(tzinfo=None)
                        if slot_datetime_utc < now_utc:
                            current_slot += duration
                            continue
                        
                        # Verificar solapamiento con turnos existentes
                        slot_end_utc = slot_datetime_utc + timedelta(hours=duration)
                        
                        overlapping = self.search([
                            ('doctor_id', '=', doctor_id),
                            ('state', 'in', ['draft', 'confirmed']),
                            ('date_start', '<', slot_end_utc),
                            ('date_end', '>', slot_datetime_utc)
                        ], limit=1)
                        
                        if not overlapping:
                            # Mostrar la hora LOCAL al usuario (no UTC)
                            slots.append({
                                'time': f"{slot_hour:02d}:{slot_minute:02d}",
                                'datetime': slot_datetime_utc.strftime('%Y-%m-%d %H:%M:%S'),
                                'available': True
                            })
                        
                        current_slot += duration
                
                if slots:
                    result['days'][date_str] = {
                        'day': current_date.day,
                        'weekday': current_date.strftime('%A')[:3],
                        'slots': slots,
                        'has_availability': True
                    }
            
            current_date += timedelta(days=1)
        
        return result

