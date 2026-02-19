# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalSpecialty(models.Model):
    _name = 'medical.specialty'
    _description = 'Especialidad Médica'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
        help='Nombre de la especialidad médica'
    )
    code = fields.Char(
        string='Código',
        required=True,
        size=10,
        help='Código corto de la especialidad (ej: co, of, cg)'
    )
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color para identificar la especialidad en el sistema'
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está inactivo, la especialidad no se podrá usar'
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'El código de la especialidad debe ser único.'),
    ]

    @api.constrains('code')
    def _check_code(self):
        """Validar que el código no esté vacío y tenga formato correcto"""
        for record in self:
            if record.code:
                if not record.code.strip():
                    raise ValidationError(_('El código no puede estar vacío.'))
                if ' ' in record.code:
                    raise ValidationError(_('El código no puede contener espacios.'))
