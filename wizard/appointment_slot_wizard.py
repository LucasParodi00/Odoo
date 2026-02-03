# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AppointmentSlotLine(models.TransientModel):
    """Línea de slot de horario disponible"""
    _name = 'appointment.slot.line'
    _description = 'Línea de Horario Disponible'
    
    wizard_id = fields.Many2one('appointment.slot.wizard', string='Wizard', required=True, ondelete='cascade')
    slot_time = fields.Char(string='Hora', required=True)
    slot_datetime = fields.Datetime(string='Fecha y Hora', required=True)
    
    def name_get(self):
        """Mostrar hora en el campo selection"""
        result = []
        for line in self:
            name = f"⏰ {line.slot_time}"
            result.append((line.id, name))
        return result


class AppointmentSlotWizard(models.TransientModel):
    """Wizard para seleccionar fecha y hora del turno de forma interactiva"""
    _name = 'appointment.slot.wizard'
    _description = 'Asistente de Selección de Horario'

    appointment_id = fields.Many2one('medical.appointment', string='Turno', required=True, ondelete='cascade')
    doctor_id = fields.Many2one('medical.doctor', related='appointment_id.doctor_id', readonly=True)
    specialty_id = fields.Many2one('medical.specialty', related='appointment_id.specialty_id', readonly=True)
    practice_id = fields.Many2one('medical.practice', related='appointment_id.practice_id', readonly=True)
    
    # Control de mes/año
    current_year = fields.Integer(string='Año', default=lambda self: datetime.now().year)
    current_month = fields.Integer(string='Mes', default=lambda self: datetime.now().month)
    
    month_display = fields.Char(string='Mes Actual', compute='_compute_month_display', store=False)
    
    # Paso 1: Selección de día
    available_date = fields.Date(
        string='Seleccione el Día',
        help='Elija una fecha con disponibilidad'
    )
    
    available_dates_html = fields.Html(
        string='Días Disponibles',
        compute='_compute_available_dates_html',
        sanitize=False
    )
    
    # Paso 2: Selección de horario
    available_slots_html = fields.Html(
        string='Horarios Disponibles',
        compute='_compute_available_slots_html',
        sanitize=False
    )
    
    available_slot_ids = fields.One2many(
        'appointment.slot.line',
        'wizard_id',
        string='Horarios',
        compute='_compute_available_slot_ids'
    )
    
    selected_slot_id = fields.Many2one(
        'appointment.slot.line',
        string='Horario Seleccionado',
        domain="[('wizard_id', '=', id)]"
    )

    @api.depends('current_year', 'current_month')
    def _compute_month_display(self):
        month_names = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        for wizard in self:
            if wizard.current_month and wizard.current_year:
                wizard.month_display = f"{month_names[wizard.current_month - 1]} {wizard.current_year}"
            else:
                wizard.month_display = ""

    @api.depends('doctor_id', 'specialty_id', 'practice_id', 'current_year', 'current_month')
    def _compute_available_dates_html(self):
        """Muestra calendario con días disponibles"""
        for wizard in self:
            if not wizard.doctor_id or not wizard.specialty_id or not wizard.practice_id:
                wizard.available_dates_html = '<div class="alert alert-info">Complete los datos del turno primero</div>'
                continue
            
            # Obtener slots disponibles para el mes actual
            slots_data = wizard.appointment_id.get_available_slots(
                wizard.doctor_id.id,
                wizard.specialty_id.id,
                wizard.practice_id.id,
                wizard.current_year,
                wizard.current_month
            )
            
            wizard.available_dates_html = wizard._generate_calendar_html(slots_data, wizard.current_year, wizard.current_month)
    
    @api.depends('available_date', 'doctor_id', 'specialty_id', 'practice_id', 'current_year', 'current_month')
    def _compute_available_slot_ids(self):
        """Genera las líneas de horarios disponibles para el día seleccionado"""
        slot_line_obj = self.env['appointment.slot.line']
        
        for wizard in self:
            # Limpiar slots existentes
            wizard.available_slot_ids.unlink()
            
            if not wizard.available_date:
                continue
            
            if not wizard.doctor_id or not wizard.specialty_id or not wizard.practice_id:
                continue
            
            # Obtener año y mes de la fecha seleccionada
            year = wizard.available_date.year
            month = wizard.available_date.month
            
            # Obtener slots del mes
            slots_data = wizard.appointment_id.get_available_slots(
                wizard.doctor_id.id,
                wizard.specialty_id.id,
                wizard.practice_id.id,
                year,
                month
            )
            
            # Filtrar solo el día seleccionado
            date_str = wizard.available_date.strftime('%Y-%m-%d')
            day_data = slots_data.get('days', {}).get(date_str, {})
            slots_list = day_data.get('slots', [])
            
            # Crear líneas para cada slot
            for slot in slots_list:
                slot_time = slot.get('time', '')
                slot_datetime_str = slot.get('datetime', '')
                
                if slot_time and slot_datetime_str:
                    slot_dt = datetime.strptime(slot_datetime_str, '%Y-%m-%d %H:%M:%S')
                    slot_line_obj.create({
                        'wizard_id': wizard.id,
                        'slot_time': slot_time,
                        'slot_datetime': slot_dt,
                    })
    
    @api.depends('available_date', 'available_slot_ids')
    def _compute_available_slots_html(self):
        """Muestra horarios del día seleccionado"""
        for wizard in self:
            if not wizard.available_date:
                wizard.available_slots_html = '<div class="alert alert-info">👆 Primero seleccione un día del calendario arriba</div>'
                continue
            
            if not wizard.available_slot_ids:
                wizard.available_slots_html = '<div class="alert alert-warning">No hay horarios disponibles para este día</div>'
                continue
            
            # Generar HTML informativo
            date_obj = wizard.available_date
            day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            day_name = day_names[date_obj.weekday()]
            formatted_date = f"{day_name} {date_obj.day}/{date_obj.month}/{date_obj.year}"
            
            html = f'''
            <div style="margin: 20px 0; font-family: Arial, sans-serif;">
                <h5 style="text-align: center; color: #28a745; margin-bottom: 20px;">
                    🗓️ {formatted_date}
                </h5>
                <div style="background: #e8f5e9; padding: 20px; border-radius: 10px; text-align: center;">
                    <p style="font-size: 16px; color: #2e7d32; margin: 0;">
                        <strong>✓ {len(wizard.available_slot_ids)} horarios disponibles</strong>
                    </p>
                    <p style="font-size: 14px; color: #666; margin-top: 10px;">
                        Seleccione uno en el campo "Horario Seleccionado" abajo
                    </p>
                </div>
            </div>
            '''
            
            wizard.available_slots_html = html
    
    def _generate_calendar_html(self, slots_data, year, month):
        """Genera HTML del calendario sin JavaScript"""
        if not slots_data or not slots_data.get('days'):
            return '<div class="alert alert-warning">No hay horarios disponibles para este mes</div>'
        
        from calendar import monthrange
        num_days = monthrange(year, month)[1]
        first_weekday = monthrange(year, month)[0]
        
        month_names = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        html = f'''
        <div style="margin: 20px 0; font-family: Arial, sans-serif;">
            <h4 style="text-align: center; margin-bottom: 20px; color: #333;">
                📅 {month_names[month-1]} {year}
            </h4>
            
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-bottom: 10px;">
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Lun</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Mar</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Mié</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Jue</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Vie</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Sáb</div>
                <div style="text-align: center; font-weight: bold; padding: 5px; background: #f0f0f0; border-radius: 3px;">Dom</div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px;">
        '''
        
        for _ in range(first_weekday):
            html += '<div></div>'
        
        for day in range(1, num_days + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            day_data = slots_data['days'].get(date_str, {})
            has_slots = day_data.get('has_availability', False)
            
            if has_slots:
                slots_count = len(day_data.get('slots', []))
                # Día disponible - se puede seleccionar
                html += f'''
                <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border: 2px solid #28a745; border-radius: 8px; padding: 10px; text-align: center; font-weight: bold;">
                    <div style="font-size: 18px;">{day}</div>
                    <div style="font-size: 10px; color: #28a745; margin-top: 3px;">✓ {slots_count} turnos</div>
                </div>
                '''
            else:
                html += f'''
                <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 10px; text-align: center; color: #999; font-size: 18px;">
                    {day}
                </div>
                '''
        
        html += '''
            </div>
            <div style="margin-top: 15px; padding: 10px; background: #e3f2fd; border-radius: 5px; text-align: center;">
                💡 <strong>Seleccione un día VERDE en el campo "Seleccione el Día" de arriba</strong>
            </div>
        </div>
        '''
        
        return html
    
    def _generate_slots_html(self, day_data, date_str):
        """Genera HTML con botones para cada horario - sin JavaScript"""
        slots_list = day_data.get('slots', [])
        
        if not slots_list:
            return '<div class="alert alert-warning">No hay horarios disponibles</div>'
        
        # Convertir fecha a formato legible
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        day_name = day_names[date_obj.weekday()]
        formatted_date = f"{day_name} {date_obj.day}/{date_obj.month}/{date_obj.year}"
        
        html = f'''
        <div style="margin: 20px 0; font-family: Arial, sans-serif;">
            <h5 style="text-align: center; color: #28a745; margin-bottom: 20px;">
                🗓️ {formatted_date}
            </h5>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
        '''
        
        # Crear lista de horarios en formato de selección
        html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; text-align: center;">'
        
        for idx, slot in enumerate(slots_list):
            slot_time = slot.get('time', '')
            slot_datetime = slot.get('datetime', '')
            
            if slot_time and slot_datetime:
                html += f'''
                <div style="background: #e8f5e9; border: 2px solid #4caf50; border-radius: 8px; padding: 15px; font-size: 16px; font-weight: bold; color: #2e7d32; cursor: pointer;">
                    ⏰ {slot_time}
                    <br/><small style="font-size: 10px; color: #666; font-weight: normal;">{slot_datetime}</small>
                </div>
                '''
        
        html += '''
                </div>
                <div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 5px; text-align: center;">
                    💡 <strong>Seleccione uno de los horarios arriba en el campo "Horario Seleccionado" y presione "Confirmar"</strong>
                </div>
            </div>
        </div>
        '''
        
        return html
    
    # Generar lista de selección para horarios
    def _get_available_datetime_selection(self):
        """Genera lista de opciones para campo selection"""
        if not self.available_date or not self.doctor_id:
            return []
        
        today = datetime.now()
        year = today.year
        month = today.month
        
        slots_data = self.appointment_id.get_available_slots(
            self.doctor_id.id,
            self.specialty_id.id,
            self.practice_id.id,
            year,
            month
        )
        
        date_str = self.available_date.strftime('%Y-%m-%d')
        day_data = slots_data.get('days', {}).get(date_str, {})
        slots_list = day_data.get('slots', [])
        
        options = []
        for slot in slots_list:
            slot_time = slot.get('time', '')
            slot_datetime_str = slot.get('datetime', '')
            if slot_time and slot_datetime_str:
                # Convertir string a datetime
                slot_dt = datetime.strptime(slot_datetime_str, '%Y-%m-%d %H:%M:%S')
                options.append((slot_datetime_str, f"⏰ {slot_time}"))
        
        return options
    
    available_datetime_selection = fields.Selection(
        selection='_get_available_datetime_selection',
        string='Horario Seleccionado',
        help='Elija uno de los horarios disponibles'
    )
    
    def action_confirm_slot(self):
        """Confirmar horario seleccionado y volver al turno"""
        self.ensure_one()
        
        if not self.available_datetime_selection:
            from odoo.exceptions import UserError
            raise UserError(_('Debe seleccionar un día y un horario del listado.'))
        
        # Convertir string a datetime
        selected_dt = datetime.strptime(self.available_datetime_selection, '%Y-%m-%d %H:%M:%S')
        
        # Actualizar el turno con el horario seleccionado
        self.appointment_id.write({
            'date_start': selected_dt,
        })
        
        return {'type': 'ir.actions.act_window_close'}
