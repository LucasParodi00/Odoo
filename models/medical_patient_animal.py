# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MedicalPatientAnimal(models.Model):
    """
    Pacientes Animales - Para clínicas veterinarias.
    """
    _name = 'medical.patient.animal'
    _description = 'Paciente Animal'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
        help='Nombre del animal'
    )
    
    owner_id = fields.Many2one(
        'res.partner',
        string='Dueño/Tutor',
        required=True,
        ondelete='restrict',
        tracking=True,
        help='Contacto responsable del animal'
    )
    
    species = fields.Selection([
        ('dog', 'Perro'),
        ('cat', 'Gato'),
        ('bird', 'Ave'),
        ('rabbit', 'Conejo'),
        ('hamster', 'Hámster'),
        ('reptile', 'Reptil'),
        ('fish', 'Pez'),
        ('horse', 'Caballo'),
        ('cow', 'Vaca'),
        ('pig', 'Cerdo'),
        ('sheep', 'Oveja'),
        ('goat', 'Cabra'),
        ('other', 'Otro')
    ], string='Especie', required=True, tracking=True)
    
    breed = fields.Char(
        string='Raza',
        tracking=True
    )
    
    gender = fields.Selection([
        ('male', 'Macho'),
        ('female', 'Hembra'),
        ('unknown', 'Desconocido')
    ], string='Sexo', default='unknown', tracking=True)
    
    birth_date = fields.Date(
        string='Fecha de Nacimiento',
        tracking=True
    )
    
    age = fields.Char(
        string='Edad',
        compute='_compute_age',
        help='Edad calculada automáticamente'
    )
    
    weight = fields.Float(
        string='Peso (kg)',
        tracking=True,
        help='Peso actual del animal en kilogramos'
    )
    
    color = fields.Char(
        string='Color',
        tracking=True
    )
    
    microchip = fields.Char(
        string='Microchip',
        tracking=True,
        help='Número de microchip de identificación'
    )
    
    castrated = fields.Boolean(
        string='Castrado/Esterilizado',
        tracking=True
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True
    )
    
    notes = fields.Text(
        string='Observaciones',
        help='Notas adicionales sobre el animal'
    )
    
    photo = fields.Image(
        string='Foto',
        max_width=1024,
        max_height=1024
    )
    
    # Relaciones
    appointment_ids = fields.One2many(
        'medical.appointment',
        'patient_animal_id',
        string='Turnos'
    )
    
    clinical_history_ids = fields.One2many(
        'medical.clinical.history',
        'patient_animal_id',
        string='Historias Clínicas'
    )
    
    # Contadores
    appointment_count = fields.Integer(
        string='Cantidad de Turnos',
        compute='_compute_appointment_count'
    )
    
    clinical_history_count = fields.Integer(
        string='Cantidad de HC',
        compute='_compute_clinical_history_count'
    )
    
    @api.depends('birth_date')
    def _compute_age(self):
        for animal in self:
            if animal.birth_date:
                today = fields.Date.today()
                delta = today - animal.birth_date
                years = delta.days // 365
                months = (delta.days % 365) // 30
                
                if years > 0:
                    animal.age = f'{years} año{"s" if years > 1 else ""}'
                    if months > 0:
                        animal.age += f' y {months} mes{"es" if months > 1 else ""}'
                elif months > 0:
                    animal.age = f'{months} mes{"es" if months > 1 else ""}'
                else:
                    animal.age = f'{delta.days} día{"s" if delta.days > 1 else ""}'
            else:
                animal.age = ''
    
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for animal in self:
            animal.appointment_count = len(animal.appointment_ids)
    
    @api.depends('clinical_history_ids')
    def _compute_clinical_history_count(self):
        for animal in self:
            animal.clinical_history_count = len(animal.clinical_history_ids)
    
    def action_view_appointments(self):
        """Acción para ver turnos de este animal"""
        self.ensure_one()
        return {
            'name': 'Turnos',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.appointment',
            'view_mode': 'list,form,calendar',
            'domain': [('patient_animal_id', '=', self.id)],
            'context': {'default_patient_animal_id': self.id, 'default_patient_type': 'animal'}
        }
    
    def action_view_clinical_history(self):
        """Acción para ver historia clínica de este animal"""
        self.ensure_one()
        return {
            'name': 'Historia Clínica',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.clinical.history',
            'view_mode': 'list,form',
            'domain': [('patient_animal_id', '=', self.id)],
            'context': {'default_patient_animal_id': self.id}
        }
    
    def name_get(self):
        """Mostrar nombre del animal con su dueño"""
        result = []
        for animal in self:
            name = f'{animal.name} ({animal.owner_id.name})'
            result.append((animal.id, name))
        return result
    
    _sql_constraints = [
        ('microchip_unique', 'UNIQUE(microchip)', 
         'El número de microchip debe ser único.')
    ]
