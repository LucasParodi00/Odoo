# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MedicalSpecialty(models.Model):
    """
    Especialidades médicas - Punto de inicio obligatorio del flujo de turnos.
    Puede ser para clínicas médicas o veterinarias.
    """
    _name = 'medical.specialty'
    _description = 'Especialidad Médica'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
        help='Nombre de la especialidad (ej. Clínica General, Cirugía, Patología)'
    )
    
    code = fields.Char(
        string='Código',
        tracking=True,
        help='Código único de la especialidad'
    )
    
    description = fields.Text(
        string='Descripción',
        help='Descripción detallada de la especialidad'
    )
    
    patient_type = fields.Selection([
        ('person', 'Persona'),
        ('animal', 'Animal'),
        ('both', 'Ambos')
    ], string='Tipo de Paciente', required=True, default='person', tracking=True,
       help='Define qué tipo de pacientes pueden atenderse en esta especialidad')
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True
    )
    
    color = fields.Integer(
        string='Color',
        help='Color para identificación visual'
    )
    
    # Relaciones
    doctor_ids = fields.Many2many(
        'medical.doctor',
        'medical_specialty_doctor_rel',
        'specialty_id',
        'doctor_id',
        string='Médicos',
        help='Médicos que atienden esta especialidad'
    )
    
    practice_ids = fields.One2many(
        'medical.practice',
        'specialty_id',
        string='Prácticas/Atenciones',
        help='Atenciones disponibles en esta especialidad'
    )
    
    appointment_ids = fields.One2many(
        'medical.appointment',
        'specialty_id',
        string='Turnos'
    )
    
    # Contadores
    doctor_count = fields.Integer(
        string='Cantidad de Médicos',
        compute='_compute_doctor_count'
    )
    
    practice_count = fields.Integer(
        string='Cantidad de Prácticas',
        compute='_compute_practice_count'
    )
    
    appointment_count = fields.Integer(
        string='Cantidad de Turnos',
        compute='_compute_appointment_count'
    )
    
    @api.depends('doctor_ids')
    def _compute_doctor_count(self):
        for specialty in self:
            specialty.doctor_count = len(specialty.doctor_ids)
    
    @api.depends('practice_ids')
    def _compute_practice_count(self):
        for specialty in self:
            specialty.practice_count = len(specialty.practice_ids)
    
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for specialty in self:
            specialty.appointment_count = len(specialty.appointment_ids)
    
    def action_view_doctors(self):
        """Acción para ver médicos de esta especialidad"""
        self.ensure_one()
        return {
            'name': 'Médicos',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.doctor',
            'view_mode': 'kanban,list,form',
            'domain': [('specialty_ids', 'in', self.id)],
            'context': {'default_specialty_ids': [(6, 0, [self.id])]}
        }
    
    def action_view_practices(self):
        """Acción para ver prácticas de esta especialidad"""
        self.ensure_one()
        return {
            'name': 'Prácticas',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.practice',
            'view_mode': 'list,form',
            'domain': [('specialty_id', '=', self.id)],
            'context': {'default_specialty_id': self.id}
        }
    
    def action_view_appointments(self):
        """Acción para ver turnos de esta especialidad"""
        self.ensure_one()
        return {
            'name': 'Turnos',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.appointment',
            'view_mode': 'list,form,calendar',
            'domain': [('specialty_id', '=', self.id)],
            'context': {'default_specialty_id': self.id}
        }
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'El código de la especialidad debe ser único.')
    ]
