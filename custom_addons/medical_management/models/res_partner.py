# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_doctor = fields.Boolean(
        string='Es Médico',
        default=False,
        help='Marque esta opción si el contacto es un médico'
    )
    is_patient = fields.Boolean(
        string='Es Paciente',
        default=False,
        help='Marque esta opción si el contacto es un paciente'
    )
    doctor_license_number = fields.Char(
        string='N° de Matrícula',
        help='Número de matrícula profesional del médico',
        tracking=True
    )
    doctor_dni = fields.Char(
        string='DNI/CUIL',
        help='Documento Nacional de Identidad o CUIL del médico',
        tracking=True
    )
    doctor_specialty_line_ids = fields.One2many(
        'medical.doctor.specialty',
        'doctor_id',
        string='Especialidades del Médico',
        help='Especialidades médicas del profesional con duración de turnos'
    )
    doctor_specialty_ids = fields.Many2many(
        'medical.specialty',
        string='Especialidades',
        compute='_compute_doctor_specialty_ids',
        store=False,
        help='Lista de especialidades activas (campo computado para compatibilidad)'
    )
    doctor_schedule_ids = fields.One2many(
        'medical.schedule',
        'doctor_id',
        string='Agendas',
        help='Agendas del médico'
    )
    
    # Campos de Paciente
    patient_dni = fields.Char(
        string='DNI/CUIL',
        help='Documento Nacional de Identidad o CUIL del paciente',
        tracking=True
    )
    patient_birthdate = fields.Date(
        string='Fecha de Nacimiento',
        help='Fecha de nacimiento del paciente',
        tracking=True
    )
    patient_age = fields.Char(
        string='Edad',
        compute='_compute_patient_age',
        store=False,
        help='Edad calculada automáticamente desde la fecha de nacimiento'
    )
    patient_pet_ids = fields.One2many(
        'medical.patient.pet',
        'owner_id',
        string='Mascotas',
        help='Mascotas del paciente'
    )
    
    @api.depends('patient_birthdate')
    def _compute_patient_age(self):
        """Calcular edad desde la fecha de nacimiento"""
        for record in self:
            if record.patient_birthdate:
                today = date.today()
                born = record.patient_birthdate
                age = relativedelta(today, born)
                
                if age.years > 0:
                    record.patient_age = f"{age.years} año{'s' if age.years != 1 else ''}"
                    if age.months > 0:
                        record.patient_age += f" y {age.months} mes{'es' if age.months != 1 else ''}"
                elif age.months > 0:
                    record.patient_age = f"{age.months} mes{'es' if age.months != 1 else ''}"
                elif age.days > 0:
                    record.patient_age = f"{age.days} día{'s' if age.days != 1 else ''}"
                else:
                    record.patient_age = "Recién nacido"
            else:
                record.patient_age = False
    
    @api.depends('doctor_specialty_line_ids', 'doctor_specialty_line_ids.active', 'doctor_specialty_line_ids.specialty_id')
    def _compute_doctor_specialty_ids(self):
        """Calcular especialidades activas desde las líneas"""
        for record in self:
            active_specialties = record.doctor_specialty_line_ids.filtered(lambda l: l.active)
            record.doctor_specialty_ids = active_specialties.mapped('specialty_id')
    
    @api.constrains('doctor_license_number', 'is_doctor')
    def _check_doctor_license(self):
        """Validar que si es médico tenga matrícula"""
        for record in self:
            if record.is_doctor and record.doctor_license_number:
                # Verificar que no haya otro médico con la misma matrícula
                existing = self.search([
                    ('id', '!=', record.id),
                    ('doctor_license_number', '=', record.doctor_license_number),
                    ('is_doctor', '=', True)
                ])
                if existing:
                    raise ValidationError(
                        _('Ya existe un médico con la matrícula %s: %s') % 
                        (record.doctor_license_number, existing[0].name)
                    )

    @api.onchange('is_doctor')
    def _onchange_is_doctor(self):
        """Limpiar campos de médico si se desmarca la opción"""
        if not self.is_doctor:
            self.doctor_license_number = False
            self.doctor_dni = False
            self.doctor_specialty_line_ids = [(5, 0, 0)]

    @api.onchange('is_patient')
    def _onchange_is_patient(self):
        """Limpiar campos de paciente si se desmarca la opción"""
        if not self.is_patient:
            self.patient_dni = False
            self.patient_birthdate = False
