# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Turnos',
    'version': '18.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Sistema de gestión de turnos médicos con slots automáticos',
    'description': """
        Gestión de Turnos Médicos
        ==========================
        * Generación automática de slots basada en agendas médicas
        * Sistema de reserva de turnos por especialidad
        * Calendario profesional con FullCalendar
        * Búsqueda de médicos por especialidad
        * Gestión completa del flujo de turnos
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'depends': ['medical_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/appointment_slot_views.xml',
        'views/medical_appointment_views.xml',
        'wizards/appointment_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'gestion_turnos/static/lib/fullcalendar/index.global.min.js',
            # 'gestion_turnos/static/lib/fullcalendar/locales/es.global.min.js',
            'gestion_turnos/static/src/js/appointment_calendar.js',
            'gestion_turnos/static/src/css/appointment_calendar.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
}
