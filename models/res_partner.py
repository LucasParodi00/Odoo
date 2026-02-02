# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    """
    Extensión del modelo res.partner para agregar información de pacientes.
    """
    _inherit = 'res.partner'

    is_patient = fields.Boolean(
        string='Es Paciente',
        help='Indica si este contacto es paciente'
    )
    
    # Relaciones con turnos
    appointment_ids = fields.One2many(
        'medical.appointment',
        'patient_id',
        string='Turnos Médicos'
    )
    
    appointment_count = fields.Integer(
        string='Cantidad de Turnos',
        compute='_compute_appointment_count'
    )
    
    # Relaciones con historias clínicas
    clinical_history_ids = fields.One2many(
        'medical.clinical.history',
        'patient_id',
        string='Historias Clínicas'
    )
    
    clinical_history_count = fields.Integer(
        string='Cantidad de HC',
        compute='_compute_clinical_history_count'
    )
    
    # Relaciones con animales (si es dueño)
    animal_ids = fields.One2many(
        'medical.patient.animal',
        'owner_id',
        string='Animales'
    )
    
    animal_count = fields.Integer(
        string='Cantidad de Animales',
        compute='_compute_animal_count'
    )
    
    def _compute_appointment_count(self):
        for partner in self:
            partner.appointment_count = len(partner.appointment_ids)
    
    def _compute_clinical_history_count(self):
        for partner in self:
            partner.clinical_history_count = len(partner.clinical_history_ids)
    
    def _compute_animal_count(self):
        for partner in self:
            partner.animal_count = len(partner.animal_ids)
    
    def action_view_appointments(self):
        """Ver turnos del paciente"""
        self.ensure_one()
        return {
            'name': 'Turnos',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.appointment',
            'view_mode': 'tree,form,calendar',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
    
    def action_view_clinical_history(self):
        """Ver historias clínicas del paciente"""
        self.ensure_one()
        return {
            'name': 'Historias Clínicas',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.clinical.history',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
    
    def action_view_animals(self):
        """Ver animales del dueño"""
        self.ensure_one()
        return {
            'name': 'Animales',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.patient.animal',
            'view_mode': 'tree,form',
            'domain': [('owner_id', '=', self.id)],
            'context': {'default_owner_id': self.id},
        }
