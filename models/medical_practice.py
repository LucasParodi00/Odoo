# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalPractice(models.Model):
    """
    Prácticas o Atenciones Médicas.
    Define el tipo de atención que se brinda (consulta, castración, curación, etc.)
    """
    _name = 'medical.practice'
    _description = 'Práctica / Atención Médica'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
        help='Nombre de la práctica (ej. Consulta Clínica, Castración, Curación)'
    )
    
    code = fields.Char(
        string='Código',
        tracking=True,
        help='Código único de la práctica'
    )
    
    description = fields.Text(
        string='Descripción',
        help='Descripción detallada de la práctica'
    )
    
    specialty_id = fields.Many2one(
        'medical.specialty',
        string='Especialidad',
        required=True,
        ondelete='restrict',
        tracking=True,
        help='Especialidad a la que pertenece esta práctica'
    )
    
    duration = fields.Float(
        string='Duración (horas)',
        required=True,
        default=0.5,
        tracking=True,
        help='Duración estimada de la atención en horas (ej. 0.5 = 30 minutos, 2 = 2 horas)'
    )
    
    duration_minutes = fields.Integer(
        string='Duración (minutos)',
        compute='_compute_duration_minutes',
        store=True,
        help='Duración en minutos para facilitar cálculos'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True
    )
    
    color = fields.Integer(
        string='Color',
        related='specialty_id.color',
        store=True,
        readonly=True
    )
    
    # Relaciones
    appointment_ids = fields.One2many(
        'medical.appointment',
        'practice_id',
        string='Turnos'
    )
    
    # Contadores
    appointment_count = fields.Integer(
        string='Cantidad de Turnos',
        compute='_compute_appointment_count'
    )
    
    @api.depends('duration')
    def _compute_duration_minutes(self):
        for practice in self:
            practice.duration_minutes = int(practice.duration * 60)
    
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for practice in self:
            practice.appointment_count = len(practice.appointment_ids)
    
    def action_view_appointments(self):
        """Acción para ver turnos de esta práctica"""
        self.ensure_one()
        return {
            'name': 'Turnos',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.appointment',
            'view_mode': 'list,form,calendar',
            'domain': [('practice_id', '=', self.id)],
            'context': {'default_practice_id': self.id}
        }
    
    @api.constrains('duration')
    def _check_duration(self):
        for practice in self:
            if practice.duration <= 0:
                raise ValidationError(_('La duración debe ser mayor a 0.'))
            if practice.duration > 24:
                raise ValidationError(_('La duración no puede superar las 24 horas.'))
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'El código de la práctica debe ser único.')
    ]
