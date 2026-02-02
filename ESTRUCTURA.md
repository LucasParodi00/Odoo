# 🏥 Módulo de Gestión de Turnos Médicos - Odoo v18

## 📁 Estructura Completa del Módulo

```
medical_appointments/
│
├── 📄 __init__.py                          # Inicializador principal
├── 📄 __manifest__.py                      # Manifiesto del módulo
├── 📄 README.md                            # Documentación general
├── 📄 ELEMENTOS_XML.md                     # Análisis de elementos XML
├── 📄 INSTALACION.md                       # Guía de instalación y pruebas
│
├── 📂 models/                              # Modelos de datos (Python)
│   ├── __init__.py                         # Inicializador de modelos
│   ├── medical_specialty.py               # ⭐ Especialidades médicas
│   ├── medical_practice.py                # 🩺 Prácticas/Atenciones
│   ├── medical_doctor.py                  # 👨‍⚕️ Médicos
│   ├── medical_schedule.py                # 📅 Agendas médicas
│   ├── medical_schedule_line.py           # ⏰ Líneas de horarios
│   ├── medical_schedule_block.py          # 🚫 Bloqueos de agenda
│   ├── medical_patient_animal.py          # 🐕 Pacientes animales
│   ├── medical_appointment.py             # 📆 Turnos médicos
│   ├── medical_clinical_history.py        # 📋 Historias clínicas
│   └── res_partner.py                     # 👤 Extensión de contactos
│
├── 📂 views/                               # Vistas XML (Interfaz)
│   ├── medical_specialty_views.xml        # Vistas de especialidades
│   ├── medical_practice_views.xml         # Vistas de prácticas
│   ├── medical_doctor_views.xml           # Vistas de médicos
│   ├── medical_schedule_views.xml         # Vistas de agendas
│   ├── medical_appointment_views.xml      # Vistas de turnos
│   ├── medical_patient_animal_views.xml   # Vistas de animales
│   ├── medical_clinical_history_views.xml # Vistas de HC
│   ├── res_partner_views.xml              # Extensión de contactos
│   └── medical_menus.xml                  # 📋 Menús principales
│
├── 📂 security/                            # Seguridad y permisos
│   ├── medical_security.xml               # Grupos de acceso
│   └── ir.model.access.csv                # Permisos por modelo
│
├── 📂 data/                                # Datos iniciales
│   ├── medical_specialty_data.xml         # Especialidades predefinidas
│   └── medical_practice_data.xml          # Prácticas predefinidas
│
├── 📂 demo/                                # Datos de demostración
│   └── medical_demo.xml                   # Médicos, pacientes, etc.
│
└── 📂 static/                              # Recursos estáticos
    └── 📂 description/
        └── icon.png                        # Ícono del módulo
```

## 🗂️ Modelos de Datos (10 modelos)

### 1. medical.specialty (Especialidades Médicas)

**Propósito:** Punto de inicio obligatorio del flujo de turnos

```python
- name: str                    # Nombre de la especialidad
- code: str                    # Código único
- patient_type: selection      # person/animal/both
- description: text            # Descripción
- doctor_ids: many2many        # Médicos que atienden
- practice_ids: one2many       # Prácticas disponibles
```

### 2. medical.practice (Prácticas/Atenciones)

**Propósito:** Tipos de atención disponibles

```python
- name: str                    # Nombre de la práctica
- code: str                    # Código único
- specialty_id: many2one       # Especialidad asociada
- duration: float              # Duración en horas
- duration_minutes: integer    # Duración en minutos (calculado)
```

### 3. medical.doctor (Médicos)

**Propósito:** Profesionales que brindan atención

```python
- name: str                    # Nombre del médico
- partner_id: many2one         # Contacto vinculado
- license_number: str          # Matrícula profesional
- specialty_ids: many2many     # Especialidades
- schedule_ids: one2many       # Agendas
- appointment_ids: one2many    # Turnos asignados
```

### 4. medical.schedule (Agenda Médica)

**Propósito:** Disponibilidad base del médico

```python
- name: str                    # Nombre de la agenda
- doctor_id: many2one          # Médico
- active: boolean              # Solo una activa por médico
- schedule_line_ids: one2many  # Líneas de horarios
- block_ids: one2many          # Bloqueos
```

### 5. medical.schedule.line (Líneas de Agenda)

**Propósito:** Rangos horarios por día

```python
- schedule_id: many2one        # Agenda
- day_of_week: selection       # 0-6 (Lun-Dom)
- hour_from: float             # Hora inicio (8.5 = 08:30)
- hour_to: float               # Hora fin
```

### 6. medical.schedule.block (Bloqueos)

**Propósito:** Períodos no disponibles

```python
- name: str                    # Motivo del bloqueo
- schedule_id: many2one        # Agenda
- block_type: selection        # vacation/absence/training/etc
- date_from: datetime          # Inicio del bloqueo
- date_to: datetime            # Fin del bloqueo
- all_day: boolean             # Todo el día
```

### 7. medical.appointment (Turnos)

**Propósito:** Citas médicas programadas

```python
- specialty_id: many2one       # Especialidad (obligatorio)
- practice_id: many2one        # Práctica
- doctor_id: many2one          # Médico
- date_start: datetime         # Fecha/hora inicio
- date_end: datetime           # Fecha/hora fin (calculado)
- patient_type: selection      # person/animal
- patient_id: many2one         # Paciente persona
- patient_animal_id: many2one  # Paciente animal
- state: selection             # draft/confirmed/attended/cancelled/absent
- clinical_history_id: many2one # HC generada
```

### 8. medical.patient.animal (Pacientes Animales)

**Propósito:** Mascotas para veterinaria

```python
- name: str                    # Nombre del animal
- owner_id: many2one           # Dueño (res.partner)
- species: selection           # dog/cat/bird/etc
- breed: str                   # Raza
- gender: selection            # male/female
- birth_date: date             # Fecha de nacimiento
- weight: float                # Peso en kg
- microchip: str               # Número de chip
- castrated: boolean           # Castrado/esterilizado
```

### 9. medical.clinical.history (Historia Clínica)

**Propósito:** Registro de atenciones

```python
- appointment_id: many2one     # Turno atendido
- date: datetime               # Fecha de atención
- specialty_id: many2one       # Especialidad
- doctor_id: many2one          # Médico
- patient_id: many2one         # Paciente persona
- patient_animal_id: many2one  # Paciente animal
- symptoms: text               # Síntomas
- physical_exam: text          # Examen físico
- diagnosis: text              # Diagnóstico
- treatment: text              # Tratamiento
- temperature: float           # Signos vitales
- blood_pressure_systolic: int
- blood_pressure_diastolic: int
- state: selection             # draft/done
```

### 10. res.partner (Extensión)

**Propósito:** Contactos como pacientes

```python
- is_patient: boolean          # Es paciente
- appointment_ids: one2many    # Turnos
- clinical_history_ids: one2many # Historias clínicas
- animal_ids: one2many         # Animales (si es dueño)
```

## 🎨 Vistas Implementadas (8 archivos XML)

| Modelo           | Tree | Form | Kanban | Calendar | Search |
| ---------------- | ---- | ---- | ------ | -------- | ------ |
| Specialty        | ✅   | ✅   | ✅     | ❌       | ✅     |
| Practice         | ✅   | ✅   | ❌     | ❌       | ✅     |
| Doctor           | ✅   | ✅   | ✅     | ❌       | ✅     |
| Schedule         | ✅   | ✅   | ❌     | ❌       | ✅     |
| Block            | ✅   | ✅   | ❌     | ✅       | ❌     |
| Appointment      | ✅   | ✅   | ✅     | ✅       | ✅     |
| Animal           | ✅   | ✅   | ✅     | ❌       | ✅     |
| Clinical History | ✅   | ✅   | ❌     | ❌       | ✅     |

**Total de vistas:** 35 vistas XML

## 🔐 Grupos de Seguridad (4 grupos)

```
┌─────────────────────────────────────────┐
│ Administrador (Manager)                 │
│ - Acceso total                          │
│ - Configuración de especialidades       │
│ - Gestión de médicos                    │
│ - Todos los permisos                    │
└────────────────┬────────────────────────┘
                 │ hereda
        ┌────────┴────────┐
        │                 │
┌───────▼────────┐  ┌────▼──────────┐
│ Recepcionista  │  │ Médico        │
│ - Crear turnos │  │ - Ver turnos  │
│ - Confirmar    │  │ - Atender     │
│ - Cancelar     │  │ - Crear HC    │
│ - Pacientes    │  │ - Su agenda   │
└───────┬────────┘  └────┬──────────┘
        │                │
        └────────┬───────┘
                 │ hereda
        ┌────────▼────────┐
        │ Usuario (Base)  │
        │ - Ver todo      │
        │ - Sin edición   │
        └─────────────────┘
```

## 📋 Menús Principales

```
Gestión Médica 🏥
│
├── Turnos 📆
│   ├── Todos los Turnos
│   └── Turnos de Hoy
│
├── Pacientes 👥
│   ├── Personas
│   └── Animales
│
├── Historias Clínicas 📋
│
├── Médicos 👨‍⚕️
│   ├── Médicos
│   ├── Agendas
│   └── Bloqueos
│
└── Configuración ⚙️ (solo admin)
    ├── Especialidades
    └── Prácticas / Atenciones
```

## 🔄 Flujos Principales

### Flujo A: Turno con Preferencia de Médico

```
1. Seleccionar Especialidad →
2. Listar Médicos de la especialidad →
3. Seleccionar Médico →
4. Ver disponibilidad del médico →
5. Seleccionar Fecha/Hora →
6. Seleccionar Paciente →
7. Confirmar Turno
```

### Flujo B: Turno sin Preferencia de Médico

```
1. Seleccionar Especialidad →
2. Seleccionar Fecha deseada →
3. Sistema muestra médicos disponibles →
4. Seleccionar Médico →
5. Seleccionar Paciente →
6. Confirmar Turno
```

### Flujo de Atención

```
Turno Confirmado →
Botón "Atender" →
Se crea Historia Clínica →
Completar HC (síntomas, diagnóstico, tratamiento) →
Finalizar HC →
Turno pasa a "Atendido"
```

## 📊 Datos Predefinidos

### Especialidades (13)

- **Médicas (8):** Clínica General, Pediatría, Cardiología, Dermatología, Ginecología, Traumatología, Oftalmología, Odontología
- **Veterinarias (4):** Veterinaria General, Cirugía Veterinaria, Animales Exóticos, Medicina Equina
- **Mixtas (1):** Patología

### Prácticas (22)

- **Médicas:** Consultas, controles, estudios, tratamientos
- **Veterinarias:** Consultas, vacunación, castración, cirugías

### Datos Demo

- 3 Médicos configurados con agendas
- 3 Pacientes personas
- 2 Pacientes animales (mascota)

## 🎯 Validaciones Implementadas

### Validaciones de Negocio

- ✅ Solo una agenda activa por médico
- ✅ No solapamiento de horarios en agenda
- ✅ No solapamiento de turnos del mismo médico
- ✅ Verificación de bloqueos de agenda
- ✅ Médico debe atender la especialidad del turno
- ✅ Tipo de paciente compatible con especialidad
- ✅ Duración de práctica > 0 y < 24 horas
- ✅ Horarios de agenda válidos (0-24)
- ✅ Fechas de bloqueo coherentes
- ✅ Matrícula única por médico

### Validaciones de Integridad

- ✅ Campos requeridos obligatorios
- ✅ Códigos únicos (especialidad, práctica)
- ✅ Referencias existentes (médico, paciente)
- ✅ Estados válidos en flujo de turnos

## 📈 Campos Computados y Automatizaciones

### Cálculos Automáticos

- Duración en minutos (desde duración en horas)
- Hora de fin del turno (fecha inicio + duración)
- Edad del animal (desde fecha nacimiento)
- Contadores de relaciones (turnos, HC, médicos, etc.)
- Agenda actual del médico
- Tipo de paciente según especialidad

### Valores por Defecto

- Estado: borrador (turnos)
- Activo: true (la mayoría de modelos)
- Fecha: hoy (historia clínica)
- Color: asignado según registro

## 🔧 Widgets Utilizados (15)

1. **statusbar** - Barra de estados del turno
2. **statinfo** - Contadores en smart buttons
3. **boolean_toggle** - Interruptor activo/inactivo
4. **many2many_tags** - Tags de especialidades
5. **float_time** - Entrada de horarios
6. **color_picker** - Selector de colores
7. **image** - Foto de animales
8. **badge** - Estados con colores
9. **phone** - Enlaces de teléfono
10. **email** - Enlaces de email
11. **many2many_binary** - Gestión de archivos adjuntos
12. **web_ribbon** - Cintas de estado
13. **date/datetime** - Selectores de fecha
14. **text** - Áreas de texto grandes
15. **selection** - Listas desplegables

## 📦 Dependencias

```python
'depends': [
    'base',      # Módulo base de Odoo
    'contacts',  # Gestión de contactos (res.partner)
    'calendar',  # Funcionalidad de calendario
    'mail',      # Sistema de mensajería y chatter
]
```

## 🚀 Características Avanzadas

### Herencia de Modelos

- `mail.thread` - Mensajería y seguimiento
- `mail.activity.mixin` - Actividades y recordatorios

### Chatter Integrado

Todos los modelos principales tienen:

- 📧 Envío de mensajes
- 📝 Registro de cambios (tracking)
- 📅 Programación de actividades
- 👥 Seguidores

### Smart Buttons

Contadores interactivos que filtran registros relacionados:

- Especialidad → Médicos, Prácticas, Turnos
- Médico → Turnos
- Paciente → Turnos, Historias Clínicas, Animales
- Animal → Turnos, Historias Clínicas

## 📊 Estadísticas del Módulo

| Métrica                         | Cantidad |
| ------------------------------- | -------- |
| **Modelos Python**              | 10       |
| **Archivos .py**                | 11       |
| **Líneas de código Python**     | ~2,500   |
| **Archivos XML**                | 12       |
| **Vistas XML**                  | 35       |
| **Líneas de código XML**        | ~2,000   |
| **Acciones**                    | 10       |
| **Menús**                       | 13       |
| **Grupos de seguridad**         | 4        |
| **Registros de acceso**         | 36       |
| **Especialidades predefinidas** | 13       |
| **Prácticas predefinidas**      | 22       |
| **Total líneas de código**      | ~4,500   |

## ✨ Próximas Mejoras Sugeridas

### Fase 2 - Mejoras Inmediatas

- [ ] Consultorios físicos (rooms)
- [ ] Múltiples turnos en un slot
- [ ] Turnos recurrentes
- [ ] Lista de espera

### Fase 3 - Integraciones

- [ ] Integración con facturación/ventas
- [ ] Órdenes de trabajo por turno
- [ ] Gestión de pagos
- [ ] Reportes financieros

### Fase 4 - Portal del Paciente

- [ ] Auto-gestión de turnos
- [ ] Visualización de HC
- [ ] Recordatorios automáticos
- [ ] Encuestas de satisfacción

### Fase 5 - Funcionalidades Avanzadas

- [ ] Telemedicina (videollamadas)
- [ ] Recetas electrónicas
- [ ] Firma digital
- [ ] Integración con laboratorios
- [ ] Stock de medicamentos
- [ ] Calendario compartido multi-consultorio

---

## 📞 Soporte

Para dudas o consultas sobre el módulo:

- 📖 Ver [README.md](README.md) para documentación general
- 🔧 Ver [INSTALACION.md](INSTALACION.md) para guía de instalación
- 📋 Ver [ELEMENTOS_XML.md](ELEMENTOS_XML.md) para análisis técnico

---

**Desarrollado para Odoo v18**  
**Licencia:** LGPL-3  
**Estado:** ✅ Producción Ready
