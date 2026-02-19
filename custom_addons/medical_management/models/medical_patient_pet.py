# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta


class MedicalPatientPet(models.Model):
    _name = 'medical.patient.pet'
    _description = 'Mascota Paciente'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre de la mascota'
    )
    owner_id = fields.Many2one(
        'res.partner',
        string='Propietario',
        required=True,
        ondelete='restrict',
        help='Propietario de la mascota'
    )
    pet_type = fields.Selection([
        ('dog', 'Perro'),
        ('cat', 'Gato'),
        ('bird', 'Ave'),
        ('rabbit', 'Conejo'),
        ('hamster', 'Hámster'),
        ('reptile', 'Reptil'),
        ('fish', 'Pez'),
        ('other', 'Otro'),
    ], string='Tipo', required=True, default='dog', help='Tipo de mascota')
    breed = fields.Char(
        string='Raza',
        help='Raza de la mascota'
    )
    birthdate = fields.Date(
        string='Fecha de Nacimiento',
        help='Fecha de nacimiento de la mascota'
    )
    age = fields.Char(
        string='Edad',
        compute='_compute_age',
        store=False,
        help='Edad calculada automáticamente desde la fecha de nacimiento'
    )
    color = fields.Char(
        string='Color',
        help='Color de la mascota'
    )
    photo = fields.Binary(
        string='Foto',
        help='Fotografía de la mascota',
        attachment=True
    )
    notes = fields.Text(
        string='Notas',
        help='Notas adicionales sobre la mascota'
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está inactivo, la mascota no aparecerá en las búsquedas normales'
    )

    _sql_constraints = [
        ('name_owner_unique', 
         'UNIQUE(name, owner_id)', 
         'Ya existe una mascota con ese nombre para este propietario.'),
    ]

    @api.depends('birthdate')
    def _compute_age(self):
        """Calcular edad desde la fecha de nacimiento"""
        for record in self:
            if record.birthdate:
                today = date.today()
                born = record.birthdate
                age = relativedelta(today, born)
                
                if age.years > 0:
                    record.age = f"{age.years} año{'s' if age.years != 1 else ''}"
                    if age.months > 0:
                        record.age += f" y {age.months} mes{'es' if age.months != 1 else ''}"
                elif age.months > 0:
                    record.age = f"{age.months} mes{'es' if age.months != 1 else ''}"
                elif age.days > 0:
                    record.age = f"{age.days} día{'s' if age.days != 1 else ''}"
                else:
                    record.age = "Recién nacido"
            else:
                record.age = False

    def name_get(self):
        """Mostrar nombre con propietario"""
        result = []
        for record in self:
            name = f"{record.name} ({record.owner_id.name})"
            result.append((record.id, name))
        return result
