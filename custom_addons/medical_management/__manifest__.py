# -*- coding: utf-8 -*-
{
    'name': 'Gestión Médica',
    'version': '18.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Sistema completo de gestión médica con médicos, pacientes y especialidades',
    'description': """
        Gestión Médica Completa
        ========================
        * Gestión de especialidades médicas
        * Gestión de médicos
        * Gestión de pacientes
        * Sistema de agendas
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'depends': ['base', 'mail', 'calendar'],
    'data': [
        'security/ir.model.access.csv',
        'views/medical_specialty_views.xml',
        'views/medical_schedule_views.xml',
        'views/medical_doctor_views.xml',
        'views/medical_patient_views.xml',
        'views/medical_patient_pet_views.xml',
        'views/medical_menu.xml',
    ],
    'demo': [
        'data/medical_specialty_demo.xml',
        'data/medical_doctor_demo.xml',
        'data/medical_schedule_demo.xml',
        'data/medical_patient_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
