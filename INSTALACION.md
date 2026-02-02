# Guía de Instalación y Prueba - Módulo de Gestión de Turnos Médicos

## 📦 Instalación

### 1. Verificar Estructura del Módulo

El módulo debe estar ubicado en:

```
d:\Odoo\odoo18\custom_addons\medical_appointments\
```

Estructura completa:

```
medical_appointments/
├── __init__.py
├── __manifest__.py
├── README.md
├── ELEMENTOS_XML.md
├── models/
│   ├── __init__.py
│   ├── medical_specialty.py
│   ├── medical_practice.py
│   ├── medical_doctor.py
│   ├── medical_schedule.py
│   ├── medical_schedule_line.py
│   ├── medical_schedule_block.py
│   ├── medical_patient_animal.py
│   ├── medical_appointment.py
│   ├── medical_clinical_history.py
│   └── res_partner.py
├── views/
│   ├── medical_specialty_views.xml
│   ├── medical_practice_views.xml
│   ├── medical_doctor_views.xml
│   ├── medical_schedule_views.xml
│   ├── medical_appointment_views.xml
│   ├── medical_patient_animal_views.xml
│   ├── medical_clinical_history_views.xml
│   ├── res_partner_views.xml
│   └── medical_menus.xml
├── security/
│   ├── medical_security.xml
│   └── ir.model.access.csv
├── data/
│   ├── medical_specialty_data.xml
│   └── medical_practice_data.xml
├── demo/
│   └── medical_demo.xml
└── static/
    └── description/
        └── icon.png
```

### 2. Actualizar Lista de Aplicaciones

**Opción A - Desde la Interfaz:**

1. Ir a **Aplicaciones**
2. Hacer clic en el menú superior (☰)
3. Seleccionar **Actualizar lista de aplicaciones**
4. Confirmar la actualización

**Opción B - Modo Desarrollador:**

```bash
# En la terminal de PowerShell
cd d:\Odoo\odoo18
python odoo-bin -c odoo.conf -d tu_base_de_datos -u all --stop-after-init
```

### 3. Instalar el Módulo

1. Ir a **Aplicaciones**
2. Buscar: `Gestión de Turnos Médicos` o `medical_appointments`
3. Hacer clic en **Instalar**

**Nota:** Si no aparece, activar el modo desarrollador:

- Ir a **Configuración** → **Activar modo desarrollador**
- En Aplicaciones, eliminar el filtro "Apps"

### 4. Verificar Instalación

Tras la instalación, debe aparecer en el menú principal:

- **Gestión Médica** (con ícono)

## 🧪 Pruebas Funcionales

### Caso de Prueba 1: Configuración Inicial

#### 1.1 Verificar Especialidades

1. Ir a **Gestión Médica → Configuración → Especialidades**
2. Verificar que se cargaron las especialidades predefinidas:
   - Clínica General (CLG)
   - Pediatría (PED)
   - Cardiología (CAR)
   - Veterinaria General (VTG)
   - etc.
3. Crear una nueva especialidad:
   - Nombre: `Kinesiología`
   - Código: `KIN`
   - Tipo de Paciente: `Persona`
   - Guardar

#### 1.2 Verificar Prácticas

1. Ir a **Gestión Médica → Configuración → Prácticas / Atenciones**
2. Verificar prácticas cargadas
3. Crear nueva práctica:
   - Nombre: `Sesión de Kinesiología`
   - Código: `KIN01`
   - Especialidad: `Kinesiología`
   - Duración: `1.0` hora
   - Guardar

### Caso de Prueba 2: Gestión de Médicos

#### 2.1 Registrar Médico

1. Ir a **Gestión Médica → Médicos → Médicos**
2. Crear nuevo médico:
   - Nombre: `Dr. Roberto Pérez`
   - Contacto: Crear nuevo o seleccionar existente
   - Matrícula: `MN99999`
   - Especialidades: Seleccionar `Clínica General` y `Cardiología`
   - Guardar

#### 2.2 Configurar Agenda

1. En el médico creado, ir a la pestaña **Agenda Actual**
2. En **Horarios de Trabajo**, agregar líneas:

   | Día       | Desde | Hasta |
   | --------- | ----- | ----- |
   | Lunes     | 08:00 | 12:00 |
   | Lunes     | 14:00 | 18:00 |
   | Miércoles | 08:00 | 12:00 |
   | Viernes   | 14:00 | 18:00 |

3. Guardar

#### 2.3 Crear Bloqueo de Agenda

1. En la pestaña **Bloqueos**, agregar:
   - Nombre: `Vacaciones de Verano`
   - Tipo: `Vacaciones`
   - Desde: Fecha futura
   - Hasta: Fecha futura + 7 días
   - Todo el día: ✓
   - Guardar

### Caso de Prueba 3: Flujo de Turnos - Paciente Persona

#### 3.1 Registrar Paciente

1. Ir a **Gestión Médica → Pacientes → Personas**
2. Crear paciente:
   - Nombre: `María González`
   - Teléfono: `+54 11 1234-5678`
   - Email: `mgonzalez@email.com`
   - Es Paciente: ✓
   - Guardar

#### 3.2 Crear Turno (Flujo A - Con preferencia de médico)

1. Ir a **Gestión Médica → Turnos → Todos los Turnos**
2. Crear nuevo turno:
   - **Especialidad:** `Clínica General`
   - **Práctica/Atención:** `Consulta General`
   - **Médico:** `Dr. Roberto Pérez` (filtrado por especialidad)
   - **Fecha/Hora Inicio:** Seleccionar fecha y hora dentro del horario de trabajo
   - **Tipo de Paciente:** `Persona` (auto-completado)
   - **Paciente (Persona):** `María González`
   - **Motivo de Consulta:** `Control de presión arterial`
   - Guardar

**Verificaciones:**

- ✅ La hora de fin se calculó automáticamente (30 min después)
- ✅ Estado: `Borrador`
- ✅ No hay errores de validación

#### 3.3 Confirmar Turno

1. Hacer clic en **Confirmar**
2. Verificar:
   - ✅ Estado cambió a `Confirmado`
   - ✅ Se registró fecha y usuario de confirmación

#### 3.4 Atender Turno

1. Hacer clic en **Atender**
2. Se abre automáticamente la Historia Clínica
3. Completar:
   - **Síntomas:** `Dolor de cabeza leve`
   - **Examen Físico:** `Paciente en buen estado general`
   - **Diagnóstico:** `Hipertensión leve controlada`
   - **Tratamiento:** `Continuar con medicación habitual, control en 3 meses`
   - **Signos Vitales:**
     - Presión Sistólica: `130`
     - Presión Diastólica: `85`
     - Frecuencia Cardíaca: `72`
   - Guardar

4. Hacer clic en **Finalizar**

**Verificaciones:**

- ✅ Turno en estado `Atendido`
- ✅ Historia Clínica creada y vinculada
- ✅ Contador de HC en paciente aumentó

### Caso de Prueba 4: Flujo de Turnos - Paciente Animal

#### 4.1 Registrar Animal

1. Ir a **Gestión Médica → Pacientes → Animales**
2. Crear animal:
   - Nombre: `Luna`
   - Dueño/Tutor: Seleccionar o crear contacto
   - Especie: `Gato`
   - Raza: `Persa`
   - Sexo: `Hembra`
   - Fecha de Nacimiento: Hace 2 años
   - Peso: `3.5` kg
   - Castrado: ✓
   - Guardar

**Verificaciones:**

- ✅ La edad se calcula automáticamente
- ✅ Se muestra como "Luna (Nombre del Dueño)"

#### 4.2 Crear Turno Veterinario

1. Ir a **Gestión Médica → Turnos → Todos los Turnos**
2. Crear turno:
   - **Especialidad:** `Veterinaria General`
   - **Práctica:** `Consulta Veterinaria`
   - **Médico:** Médico veterinario
   - **Fecha/Hora:** Dentro del horario
   - **Tipo de Paciente:** `Animal` (auto-completado)
   - **Paciente (Animal):** `Luna`
   - **Motivo:** `Control anual`
   - Guardar y Confirmar

#### 4.3 Intentar Asignar Paciente Incorrecto

1. Crear nuevo turno
2. Especialidad: `Clínica General` (para personas)
3. Práctica: `Consulta General`
4. Médico: Seleccionar
5. Tipo de Paciente: `Persona`
6. Intentar seleccionar un animal

**Verificación esperada:**

- ✅ Error de validación: "La especialidad solo atiende personas"

### Caso de Prueba 5: Validaciones de Disponibilidad

#### 5.1 Solapamiento de Turnos

1. Crear turno:
   - Médico: `Dr. Juan Martínez`
   - Fecha: `2025-02-10 10:00`
   - Guardar y Confirmar

2. Intentar crear otro turno:
   - Mismo médico
   - Fecha: `2025-02-10 10:15` (se solapa)
   - Intentar guardar

**Verificación esperada:**

- ✅ Error: "El médico ya tiene un turno en ese horario"

#### 5.2 Turno en Horario Bloqueado

1. Ir a médico con bloqueo de vacaciones
2. Intentar crear turno en fechas bloqueadas

**Verificación esperada:**

- ✅ Error: "El médico tiene un bloqueo en ese horario: Vacaciones"

#### 5.3 Médico sin Especialidad Adecuada

1. Crear turno con Especialidad: `Pediatría`
2. Intentar asignar médico que NO tiene pediatría

**Verificación esperada:**

- ✅ El médico no aparece en la lista (por domain)
- ✅ Si se fuerza, error: "El médico no atiende la especialidad Pediatría"

### Caso de Prueba 6: Vistas de Calendario

#### 6.1 Vista Calendario de Turnos

1. Ir a **Gestión Médica → Turnos**
2. Cambiar a vista **Calendario**
3. Verificar:
   - ✅ Turnos visibles en calendario
   - ✅ Colores por médico
   - ✅ Al hacer clic, se abre el turno

#### 6.2 Vista Calendario de Bloqueos

1. Ir a **Gestión Médica → Médicos → Bloqueos**
2. Vista **Calendario**
3. Verificar bloqueos visibles

### Caso de Prueba 7: Reportes y Contadores

#### 7.1 Smart Buttons en Especialidad

1. Abrir una especialidad
2. Verificar smart buttons:
   - ✅ Cantidad de médicos
   - ✅ Cantidad de prácticas
   - ✅ Cantidad de turnos
3. Hacer clic en cada uno, verificar que filtra correctamente

#### 7.2 Smart Buttons en Médico

1. Abrir un médico
2. Verificar:
   - ✅ Contador de turnos
3. Hacer clic, verificar filtro por médico

#### 7.3 Smart Buttons en Paciente

1. Abrir un paciente persona
2. Verificar:
   - ✅ Turnos
   - ✅ Historias Clínicas
   - ✅ Animales (si tiene)

### Caso de Prueba 8: Acciones de Turno

#### 8.1 Cancelar Turno

1. Abrir turno confirmado
2. Hacer clic en **Cancelar**
3. Ingresar motivo: `Paciente canceló por motivos personales`
4. Confirmar

**Verificaciones:**

- ✅ Estado: `Cancelado`
- ✅ Motivo registrado
- ✅ No se puede volver a confirmar

#### 8.2 Marcar Ausente

1. Turno confirmado no atendido
2. Hacer clic en **Marcar Ausente**

**Verificaciones:**

- ✅ Estado: `Ausente`

#### 8.3 Reprogramar

1. Turno confirmado
2. Hacer clic en **Reprogramar**
3. Se crea nuevo turno en borrador con los mismos datos
4. Turno original queda cancelado con motivo "Reprogramado"

### Caso de Prueba 9: Filtros y Búsquedas

#### 9.1 Filtros en Turnos

1. Ir a Turnos
2. Probar filtros:
   - ✅ Borradores
   - ✅ Confirmados
   - ✅ Atendidos
   - ✅ Hoy
   - ✅ Esta Semana
   - ✅ Este Mes

#### 9.2 Agrupaciones

1. Agrupar por:
   - ✅ Estado
   - ✅ Médico
   - ✅ Especialidad
   - ✅ Fecha

### Caso de Prueba 10: Seguridad y Permisos

#### 10.1 Usuario Médico

1. Crear usuario con grupo `Médico`
2. Verificar:
   - ✅ Puede ver todos los turnos
   - ✅ Puede atender turnos
   - ✅ Puede crear historias clínicas
   - ✅ NO puede crear médicos
   - ✅ NO puede configurar especialidades

#### 10.2 Usuario Recepcionista

1. Crear usuario con grupo `Recepcionista`
2. Verificar:
   - ✅ Puede crear turnos
   - ✅ Puede confirmar turnos
   - ✅ Puede cancelar turnos
   - ✅ NO puede atender turnos
   - ✅ NO puede ver historias clínicas completas

#### 10.3 Usuario Administrador

1. Usuario con grupo `Administrador`
2. Verificar acceso total

## 🐛 Debugging

### Errores Comunes

**Error: Modelo no encontrado**

- Verificar que `__init__.py` importe todos los modelos
- Reiniciar servicio Odoo

**Error: Vista no cargada**

- Verificar sintaxis XML
- Verificar referencias de action_id en menús
- Ver logs: `Settings → Technical → Logging`

**Error: Permisos**

- Verificar `ir.model.access.csv`
- Verificar grupos asignados al usuario

### Logs

Verificar logs en modo desarrollador:

```bash
python odoo-bin -c odoo.conf -d database --log-level=debug
```

## ✅ Checklist de Instalación Exitosa

- [ ] Módulo aparece en lista de aplicaciones
- [ ] Instalación sin errores
- [ ] Menú "Gestión Médica" visible
- [ ] Especialidades predefinidas cargadas
- [ ] Prácticas predefinidas cargadas
- [ ] Datos demo cargados (si se instaló con demo)
- [ ] Puede crear médico con agenda
- [ ] Puede crear turno y confirmar
- [ ] Puede atender turno y crear HC
- [ ] Vistas calendario funcionan
- [ ] Smart buttons muestran contadores
- [ ] Filtros y búsquedas operan correctamente
- [ ] Validaciones de solapamiento funcionan
- [ ] Permisos por grupo operan correctamente

## 📊 Casos de Uso Reales

### Clínica Médica

1. Configurar especialidades médicas
2. Registrar médicos con matrículas
3. Configurar horarios de atención
4. Registrar pacientes
5. Agendar consultas
6. Atender y registrar historia clínica

### Clínica Veterinaria

1. Configurar especialidades veterinarias
2. Registrar veterinarios
3. Registrar dueños y sus mascotas
4. Agendar consultas veterinarias
5. Realizar procedimientos (vacunación, castración)
6. Mantener historia clínica animal

### Centro Médico Mixto

1. Configurar ambos tipos de especialidades
2. Médicos con especialidades mixtas (patología)
3. Gestión unificada de turnos
4. Reportes consolidados

## 🎓 Conclusión

El módulo está listo para uso en producción. Cubre todos los flujos principales:

- ✅ Gestión de especialidades y prácticas
- ✅ Configuración de médicos y agendas
- ✅ Dos flujos de solicitud de turnos
- ✅ Atención de pacientes personas y animales
- ✅ Historia clínica completa
- ✅ Validaciones de disponibilidad
- ✅ Sistema de permisos robusto
- ✅ Interfaz intuitiva con calendarios

## 🚀 Próximos Pasos Sugeridos

1. **Integración con Facturación:** Vincular turnos con órdenes de venta
2. **Portal de Pacientes:** Autogestión de turnos online
3. **Notificaciones:** Email/SMS de recordatorios
4. **Reportes:** Estadísticas de atención
5. **Recetas:** Módulo de prescripción médica
6. **Stock:** Gestión de insumos médicos

---

**Documentación completa en:** `README.md` y `ELEMENTOS_XML.md`
