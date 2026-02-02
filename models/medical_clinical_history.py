# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MedicalClinicalHistory(models.Model):
    """
    Historia Clínica - Registro de atenciones médicas.
    """
    _name = 'medical.clinical.history'
    _description = 'Historia Clínica'
    _order = 'date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    display_name = fields.Char(
        string='Historia Clínica',
        compute='_compute_display_name',
        store=True
    )
    
    # Vinculación con el turno
    appointment_id = fields.Many2one(
        'medical.appointment',
        string='Turno',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    
    # Información de la atención
    date = fields.Datetime(
        string='Fecha/Hora',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    
    specialty_id = fields.Many2one(
        'medical.specialty',
        string='Especialidad',
        required=True,
        ondelete='restrict'
    )
    
    practice_id = fields.Many2one(
        'medical.practice',
        string='Práctica/Atención',
        required=True,
        ondelete='restrict'
    )
    
    doctor_id = fields.Many2one(
        'medical.doctor',
        string='Médico',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    
    # Paciente
    patient_type = fields.Selection([
        ('person', 'Persona'),
        ('animal', 'Animal')
    ], string='Tipo de Paciente', compute='_compute_patient_type', store=True)
    
    patient_id = fields.Many2one(
        'res.partner',
        string='Paciente (Persona)',
        tracking=True
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
    
    # Contenido de la historia clínica
    reason = fields.Text(
        string='Motivo de Consulta',
        related='appointment_id.reason',
        readonly=True
    )
    
    symptoms = fields.Text(
        string='Síntomas',
        tracking=True,
        help='Síntomas reportados por el paciente'
    )
    
    physical_exam = fields.Text(
        string='Examen Físico',
        tracking=True,
        help='Hallazgos del examen físico'
    )
    
    diagnosis = fields.Text(
        string='Diagnóstico',
        required=True,
        tracking=True,
        help='Diagnóstico médico'
    )
    
    treatment = fields.Text(
        string='Tratamiento',
        tracking=True,
        help='Tratamiento prescrito'
    )
    
    observations = fields.Text(
        string='Observaciones',
        tracking=True,
        help='Observaciones adicionales'
    )
    
    # Signos vitales (opcional)
    temperature = fields.Float(
        string='Temperatura (°C)',
        tracking=True
    )
    
    blood_pressure_systolic = fields.Integer(
        string='Presión Arterial Sistólica',
        tracking=True
    )
    
    blood_pressure_diastolic = fields.Integer(
        string='Presión Arterial Diastólica',
        tracking=True
    )
    
    heart_rate = fields.Integer(
        string='Frecuencia Cardíaca (lpm)',
        tracking=True
    )
    
    respiratory_rate = fields.Integer(
        string='Frecuencia Respiratoria (rpm)',
        tracking=True
    )
    
    weight = fields.Float(
        string='Peso (kg)',
        tracking=True
    )
    
    height = fields.Float(
        string='Altura (cm)',
        tracking=True
    )
    
    # Adjuntos
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'medical_clinical_history_attachment_rel',
        'clinical_history_id',
        'attachment_id',
        string='Archivos Adjuntos',
        help='Estudios, radiografías, análisis, etc.'
    )
    
    attachment_count = fields.Integer(
        string='Cantidad de Adjuntos',
        compute='_compute_attachment_count'
    )
    
    # Control
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Finalizado')
    ], string='Estado', default='draft', required=True, tracking=True)
    
    @api.depends('patient_id', 'patient_animal_id')
    def _compute_patient_type(self):
        for history in self:
            if history.patient_id:
                history.patient_type = 'person'
            elif history.patient_animal_id:
                history.patient_type = 'animal'
            else:
                history.patient_type = False
    
    @api.depends('patient_id', 'patient_animal_id', 'patient_type')
    def _compute_patient_name(self):
        for history in self:
            if history.patient_type == 'person' and history.patient_id:
                history.patient_name = history.patient_id.name
            elif history.patient_type == 'animal' and history.patient_animal_id:
                history.patient_name = history.patient_animal_id.name
            else:
                history.patient_name = ''
    
    @api.depends('specialty_id', 'patient_name', 'date', 'doctor_id')
    def _compute_display_name(self):
        for history in self:
            parts = []
            if history.specialty_id:
                parts.append(history.specialty_id.name)
            if history.patient_name:
                parts.append(history.patient_name)
            if history.date:
                parts.append(history.date.strftime('%d/%m/%Y'))
            
            history.display_name = ' - '.join(parts) if parts else _('Nueva Historia Clínica')
    
    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for history in self:
            history.attachment_count = len(history.attachment_ids)
    
    def action_done(self):
        """Finalizar historia clínica"""
        self.write({'state': 'done'})
        return True
    
    def action_view_attachments(self):
        """Ver archivos adjuntos"""
        self.ensure_one()
        return {
            'name': _('Archivos Adjuntos'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.attachment_ids.ids)],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }
