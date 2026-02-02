# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Gestión de Turnos Médicos 2',
    'version': '18.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Sistema completo de gestión de turnos médicos para clínicas y veterinarias',
    'description': """
        Gestión de Turnos Médicos
        ==========================
        
        Módulo genérico y escalable para gestión de turnos médicos, apto para:
        * Clínicas médicas
        * Clínicas veterinarias
        * Centros de salud multidisciplinarios
        
        Características principales:
        ----------------------------
        * Gestión de especialidades médicas
        * Registro y configuración de médicos
        * Agendas médicas configurables con múltiples rangos horarios
        * Sistema flexible de solicitud de turnos (con/sin preferencia de médico)
        * Gestión de pacientes humanos y animales
        * Historia clínica asociada a atenciones
        * Cálculo automático de disponibilidad
        * Bloqueos de agenda (vacaciones, ausencias)
        * Estados de turnos (confirmado, atendido, cancelado, ausente)
    """,
    'author': 'Odoo Medical',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'contacts',
        'calendar',
        'mail',
    ],
    'data': [
        # Seguridad
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        
        # Datos base
        'data/medical_specialty_data.xml',
        'data/medical_practice_data.xml',
        
        # Vistas
        'views/medical_specialty_views.xml',
        'views/medical_practice_views.xml',
        'views/medical_doctor_views.xml',
        'views/medical_schedule_views.xml',
        'views/medical_appointment_views.xml',
        'views/medical_patient_animal_views.xml',
        'views/medical_clinical_history_views.xml',
        'views/res_partner_views.xml',
        
        # Menús
        'views/medical_menus.xml',
    ],
    'demo': [
        'demo/medical_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
