# Diagramas y Relaciones del Módulo de Gestión de Turnos Médicos

## 🗺️ Diagrama de Relaciones Entre Modelos

```
                            ┌─────────────────┐
                            │ res.partner     │
                            │ (Contactos)     │
                            └────┬────────┬───┘
                                 │        │
                 ┌───────────────┘        └─────────────┐
                 │                                      │
                 │ (dueño)                             │ (paciente)
                 │                                      │
         ┌───────▼──────────┐                   ┌──────▼──────────┐
         │ medical.patient  │                   │ medical.doctor  │
         │ .animal          │                   │                 │
         │ (Animales)       │                   │ (Médicos)       │
         └────┬─────────────┘                   └───┬─────────────┘
              │                                     │
              │ (paciente)                          │ (médico)
              │                                     │
              │                              ┌──────┴──────┐
              │                              │             │
              │                         ┌────▼────┐  ┌────▼────────────┐
              │                         │ M2M     │  │ medical         │
              │                         │         │  │ .schedule       │
              │                    ┌────┤Specialty├──┤ (Agendas)       │
              │                    │    │         │  └─────┬───────────┘
              │                    │    └────┬────┘        │
              │                    │         │             │
              │               ┌────▼─────┐   │      ┌──────┴──────┐
              │               │ medical  │   │      │             │
              │               │.specialty│◄──┘  ┌───▼────┐  ┌────▼─────────┐
              │               │          │      │schedule│  │schedule.block│
              │               └────┬─────┘      │.line   │  │(Bloqueos)    │
              │                    │            └────────┘  └──────────────┘
              │                    │ (especialidad)
              │                    │
              │               ┌────▼─────┐
              │               │ medical  │
              │               │.practice │
              │               │          │
              │               └────┬─────┘
              │                    │ (práctica)
              │                    │
              └────────────────┐   │   ┌──────────────────┐
                               │   │   │                  │
                         ┌─────▼───▼───▼────┐             │
                         │ medical          │             │
                         │ .appointment     │─────────────┘
                         │ (Turnos)         │ (turno atendido)
                         └──────────────────┘
                                  │
                                  │
                         ┌────────▼──────────┐
                         │ medical.clinical  │
                         │ .history          │
                         │ (Historia Clínica)│
                         └───────────────────┘
```

## 🔄 Diagrama de Estados del Turno

```
        ┌─────────┐
        │ DRAFT   │ (Borrador)
        └────┬────┘
             │
             │ action_confirm()
             │
        ┌────▼────────┐
        │ CONFIRMED   │ (Confirmado)
        └─┬────┬────┬─┘
          │    │    │
          │    │    └──────────────┐
          │    │                   │
          │    │ action_attend()   │ action_mark_absent()
          │    │                   │
          │    │              ┌────▼────┐
          │    │              │ ABSENT  │ (Ausente)
          │    │              └─────────┘
          │    │
          │    └─────────────┐
          │                  │
          │            ┌─────▼──────┐
          │            │ ATTENDED   │ (Atendido)
          │            └────────────┘
          │
          │ action_cancel()
          │
     ┌────▼──────┐
     │ CANCELLED │ (Cancelado)
     └───────────┘
```

## 📅 Flujo de Solicitud de Turno - Tipo A (Con preferencia)

```
┌───────────────────────────────────────────────────────────┐
│ FLUJO A: Paciente con Preferencia de Médico              │
└───────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │ 1. INICIO        │
    │ Paciente accede  │
    └────────┬─────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 2. Seleccionar ESPECIALIDAD                 │
    │ - Clínica General                           │
    │ - Pediatría                                 │
    │ - Veterinaria                               │
    │ - etc.                                      │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 3. Ver MÉDICOS de la especialidad          │
    │                                             │
    │  👨‍⚕️ Dr. Juan Martínez                      │
    │  👩‍⚕️ Dra. María Gómez                       │
    │  👨‍⚕️ Dr. Carlos Fernández                   │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 4. Seleccionar MÉDICO específico           │
    │    Ejemplo: Dr. Juan Martínez               │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 5. Sistema calcula DISPONIBILIDAD          │
    │                                             │
    │ Considera:                                  │
    │ ✓ Agenda del médico (días/horarios)        │
    │ ✓ Duración de la atención                  │
    │ ✓ Turnos ya reservados                     │
    │ ✓ Bloqueos de agenda                       │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 6. Mostrar CALENDARIO con slots disponibles│
    │                                             │
    │  📅 Lunes 10/02                            │
    │     ✅ 08:00 - 08:30  disponible           │
    │     ❌ 08:30 - 09:00  ocupado              │
    │     ✅ 09:00 - 09:30  disponible           │
    │                                             │
    │  📅 Miércoles 12/02                        │
    │     ✅ 10:00 - 10:30  disponible           │
    │     ✅ 10:30 - 11:00  disponible           │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 7. Paciente selecciona FECHA y HORA        │
    │    Ejemplo: Lunes 10/02 a las 09:00        │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 8. Ingresar datos del PACIENTE             │
    │ - Seleccionar paciente existente           │
    │ - O crear nuevo paciente                   │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 9. Confirmar TURNO                         │
    │                                             │
    │ Resumen:                                    │
    │ - Especialidad: Clínica General            │
    │ - Atención: Consulta General (30 min)      │
    │ - Médico: Dr. Juan Martínez                │
    │ - Fecha: Lunes 10/02/2025                  │
    │ - Hora: 09:00 - 09:30                      │
    │ - Paciente: María González                 │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 10. Turno CONFIRMADO                       │
    │     Estado: Confirmado ✓                   │
    └─────────────────────────────────────────────┘
```

## 📅 Flujo de Solicitud de Turno - Tipo B (Sin preferencia)

```
┌───────────────────────────────────────────────────────────┐
│ FLUJO B: Paciente sin Preferencia de Médico              │
└───────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │ 1. INICIO        │
    │ Paciente accede  │
    └────────┬─────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 2. Seleccionar ESPECIALIDAD                 │
    │    Ejemplo: Clínica General                 │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 3. Seleccionar FECHA deseada                │
    │    Ejemplo: Mañana (11/02/2025)             │
    │                                             │
    │    Opcional: Franja horaria                 │
    │    ○ Mañana (08:00 - 12:00)                │
    │    ○ Tarde (14:00 - 18:00)                 │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 4. Sistema busca MÉDICOS DISPONIBLES       │
    │                                             │
    │ Filtros aplicados:                          │
    │ ✓ Atienden la especialidad                 │
    │ ✓ Trabajan en la fecha seleccionada        │
    │ ✓ Tienen slots disponibles                 │
    │ ✓ Compatible con duración de atención      │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 5. Mostrar LISTA de médicos disponibles    │
    │                                             │
    │  👨‍⚕️ Dr. Juan Martínez                      │
    │     ✅ 09:00 - 09:30  disponible           │
    │     ✅ 11:00 - 11:30  disponible           │
    │                                             │
    │  👩‍⚕️ Dra. María Gómez                       │
    │     ✅ 10:00 - 10:30  disponible           │
    │     ✅ 11:30 - 12:00  disponible           │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 6. Paciente selecciona MÉDICO y HORARIO    │
    │    Ejemplo: Dr. Juan Martínez - 09:00      │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 7. Ingresar datos del PACIENTE             │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 8. Confirmar TURNO                         │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ 9. Turno CONFIRMADO ✓                      │
    └─────────────────────────────────────────────┘
```

## 🏥 Flujo Completo de Atención Médica

```
┌────────────────────────────────────────────────────────────┐
│ CICLO COMPLETO: Desde Solicitud hasta Historia Clínica    │
└────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ SOLICITUD       │
│ Paciente        │
│ solicita turno  │
└────────┬────────┘
         │
    ┌────▼──────────────────┐
    │ TURNO CREADO          │
    │ Estado: Borrador      │
    └────────┬──────────────┘
             │
             │ Recepcionista/Sistema
             │ verifica y confirma
             │
    ┌────────▼──────────────┐
    │ TURNO CONFIRMADO      │
    │ - Fecha bloqueada     │
    │ - Paciente notificado │
    └────────┬──────────────┘
             │
             │ Día del turno
             │
    ┌────────▼───────────────────────┐
    │ PACIENTE LLEGA                 │
    │                                │
    │ ¿Está presente?                │
    └─┬──────────────────────────┬───┘
      │ NO                    SÍ │
      │                          │
┌─────▼──────┐        ┌──────────▼──────────┐
│ AUSENTE    │        │ MÉDICO ATIENDE      │
│            │        │                     │
│ Estado:    │        │ Acciones:           │
│ Ausente    │        │ 1. Revisa motivo    │
└────────────┘        │ 2. Examina paciente │
                      │ 3. Diagnostica      │
                      │ 4. Prescribe        │
                      └──────────┬──────────┘
                                 │
                      ┌──────────▼──────────┐
                      │ CREAR HC            │
                      │                     │
                      │ Sistema crea        │
                      │ automáticamente     │
                      │ historia clínica    │
                      └──────────┬──────────┘
                                 │
                      ┌──────────▼──────────┐
                      │ COMPLETAR HC        │
                      │                     │
                      │ Campos:             │
                      │ - Síntomas          │
                      │ - Examen físico     │
                      │ - Diagnóstico       │
                      │ - Tratamiento       │
                      │ - Signos vitales    │
                      │ - Adjuntos          │
                      └──────────┬──────────┘
                                 │
                      ┌──────────▼──────────┐
                      │ FINALIZAR HC        │
                      │                     │
                      │ HC Estado: Done     │
                      └──────────┬──────────┘
                                 │
                      ┌──────────▼──────────┐
                      │ TURNO ATENDIDO      │
                      │                     │
                      │ Estado: Attended    │
                      │ Vinculado a HC      │
                      └──────────┬──────────┘
                                 │
                      ┌──────────▼──────────┐
                      │ SEGUIMIENTO         │
                      │                     │
                      │ Paciente puede:     │
                      │ - Ver su HC         │
                      │ - Solicitar turno   │
                      │   de control        │
                      └─────────────────────┘
```

## 🔒 Diagrama de Permisos y Seguridad

```
┌─────────────────────────────────────────────────────────────┐
│                    MATRIZ DE PERMISOS                        │
└─────────────────────────────────────────────────────────────┘

                        │ Usuario │ Recepc. │ Médico │ Admin │
────────────────────────┼─────────┼─────────┼────────┼───────┤
Especialidades          │         │         │        │       │
  - Ver                 │    ✓    │    ✓    │   ✓    │   ✓   │
  - Crear/Editar        │    ✗    │    ✗    │   ✗    │   ✓   │
  - Eliminar            │    ✗    │    ✗    │   ✗    │   ✓   │
────────────────────────┼─────────┼─────────┼────────┼───────┤
Prácticas               │         │         │        │       │
  - Ver                 │    ✓    │    ✓    │   ✓    │   ✓   │
  - Crear/Editar        │    ✗    │    ✗    │   ✗    │   ✓   │
  - Eliminar            │    ✗    │    ✗    │   ✗    │   ✓   │
────────────────────────┼─────────┼─────────┼────────┼───────┤
Médicos                 │         │         │        │       │
  - Ver                 │    ✓    │    ✓    │   ✓    │   ✓   │
  - Crear/Editar        │    ✗    │    ✗    │   ✓**  │   ✓   │
  - Eliminar            │    ✗    │    ✗    │   ✗    │   ✓   │
────────────────────────┼─────────┼─────────┼────────┼───────┤
Agendas                 │         │         │        │       │
  - Ver                 │    ✓    │    ✓    │   ✓    │   ✓   │
  - Crear/Editar        │    ✗    │    ✗    │   ✓    │   ✓   │
  - Eliminar            │    ✗    │    ✗    │   ✓    │   ✓   │
────────────────────────┼─────────┼─────────┼────────┼───────┤
Bloqueos                │         │         │        │       │
  - Ver                 │    ✓    │    ✓    │   ✓    │   ✓   │
  - Crear/Editar        │    ✗    │    ✗    │   ✓    │   ✓   │
  - Eliminar            │    ✗    │    ✗    │   ✓    │   ✓   │
────────────────────────┼─────────┼─────────┼────────┼───────┤
Turnos                  │         │         │        │       │
  - Ver                 │    ✓    │    ✓    │   ✓    │   ✓   │
  - Crear               │    ✗    │    ✓    │   ✓    │   ✓   │
  - Editar              │    ✗    │    ✓    │   ✓    │   ✓   │
  - Confirmar           │    ✗    │    ✓    │   ✓    │   ✓   │
  - Atender             │    ✗    │    ✗    │   ✓    │   ✓   │
  - Cancelar            │    ✗    │    ✓    │   ✗    │   ✓   │
  - Eliminar            │    ✗    │    ✗    │   ✗    │   ✓   │
────────────────────────┼─────────┼─────────┼────────┼───────┤
Pacientes               │         │         │        │       │
  - Ver                 │    ✓    │    ✓    │   ✓    │   ✓   │
  - Crear/Editar        │    ✗    │    ✓    │   ✓    │   ✓   │
  - Eliminar            │    ✗    │    ✗    │   ✗    │   ✓   │
────────────────────────┼─────────┼─────────┼────────┼───────┤
Historias Clínicas      │         │         │        │       │
  - Ver                 │    ✓    │    ✓    │   ✓    │   ✓   │
  - Crear/Editar        │    ✗    │    ✗    │   ✓    │   ✓   │
  - Eliminar            │    ✗    │    ✗    │   ✗    │   ✓   │
────────────────────────┴─────────┴─────────┴────────┴───────┘

** Solo su propio registro
```

## 🧮 Cálculo de Disponibilidad de Médico

```
┌───────────────────────────────────────────────────────────┐
│ ALGORITMO: Calcular Slots Disponibles                    │
└───────────────────────────────────────────────────────────┘

INPUT:
  - Médico: Dr. Juan Martínez
  - Fecha: 10/02/2025
  - Duración práctica: 30 minutos

PASO 1: Obtener agenda activa del médico
  └─> Agenda: "Agenda - Dr. Martínez"

PASO 2: Verificar día de la semana
  └─> 10/02/2025 = Lunes (día 0)

PASO 3: Obtener horarios configurados para Lunes
  └─> schedule_lines WHERE day_of_week = '0'
      Resultado:
      - 08:00 - 12:00
      - 14:00 - 18:00

PASO 4: Generar slots de 30 minutos
  Rango 1: 08:00 - 12:00
    ├─> 08:00 - 08:30 ✓
    ├─> 08:30 - 09:00 ✓
    ├─> 09:00 - 09:30 ✓
    ├─> 09:30 - 10:00 ✓
    ├─> 10:00 - 10:30 ✓
    ├─> 10:30 - 11:00 ✓
    ├─> 11:00 - 11:30 ✓
    └─> 11:30 - 12:00 ✓

  Rango 2: 14:00 - 18:00
    ├─> 14:00 - 14:30 ✓
    ├─> 14:30 - 15:00 ✓
    └─> ... (8 slots)

PASO 5: Filtrar slots ocupados
  Buscar turnos existentes:
  WHERE doctor_id = Dr. Martínez
    AND date_start >= '2025-02-10 00:00'
    AND date_start < '2025-02-11 00:00'
    AND state IN ('draft', 'confirmed')

  Resultado: Turno de 09:00 a 09:30

  Eliminar: 09:00 - 09:30 ✗

PASO 6: Filtrar slots bloqueados
  Buscar bloqueos:
  WHERE schedule_id = Agenda Dr. Martínez
    AND date_from <= '2025-02-10 23:59'
    AND date_to >= '2025-02-10 00:00'

  Resultado: Sin bloqueos

PASO 7: Resultado final
  Slots disponibles:
  ├─> 08:00 - 08:30 ✅
  ├─> 08:30 - 09:00 ✅
  ├─> 09:30 - 10:00 ✅
  ├─> 10:00 - 10:30 ✅
  └─> ... (total: 15 slots)

OUTPUT: Lista de 15 slots disponibles
```

## 📊 Relaciones Many2many Detalladas

### medical.doctor ↔ medical.specialty

```
Tabla intermedia: medical_specialty_doctor_rel

┌──────────────┬──────────────┐
│ doctor_id    │ specialty_id │
├──────────────┼──────────────┤
│ 1 (Martínez) │ 1 (Clínica)  │
│ 1 (Martínez) │ 3 (Cardio)   │
│ 2 (Gómez)    │ 2 (Pediatría)│
│ 2 (Gómez)    │ 4 (Dermato)  │
│ 3 (Fernández)│ 9 (Vet Gen)  │
│ 3 (Fernández)│ 10 (Vet Cir) │
└──────────────┴──────────────┘

Permite:
- Un médico con múltiples especialidades
- Una especialidad atendida por múltiples médicos
```

## 🎯 Casos de Uso por Rol

### Recepcionista

```
1. Recibe llamada de paciente
   └─> Abrir "Turnos" → Crear

2. Pregunta por especialidad
   └─> Seleccionar especialidad en formulario

3. Pregunta si tiene preferencia de médico

   SI: Flujo A
   └─> Seleccionar médico
   └─> Mostrar calendario disponible
   └─> Agendar en slot específico

   NO: Flujo B
   └─> Preguntar fecha preferida
   └─> Buscar médicos disponibles
   └─> Agendar con médico disponible

4. Registrar datos del paciente
   └─> Buscar en base de datos
   └─> Si no existe, crear nuevo

5. Confirmar turno
   └─> Estado: Confirmado
   └─> Informar fecha/hora al paciente
```

### Médico

```
1. Inicio del día
   └─> Ver "Turnos de Hoy"
   └─> Vista Calendario con sus turnos

2. Llega paciente
   └─> Abrir turno confirmado
   └─> Clic en "Atender"

3. Se crea HC automáticamente
   └─> Completar síntomas
   └─> Realizar examen físico
   └─> Ingresar diagnóstico
   └─> Prescribir tratamiento
   └─> Registrar signos vitales

4. Finalizar consulta
   └─> Clic en "Finalizar"
   └─> HC estado: Done
   └─> Turno estado: Attended

5. Configurar ausencias
   └─> Ir a "Médicos" → Mi agenda
   └─> Crear bloqueo de agenda
   └─> Tipo: Vacaciones/Congreso/etc
```

### Administrador

```
1. Configuración inicial
   └─> Crear/revisar especialidades
   └─> Crear/revisar prácticas
   └─> Registrar médicos
   └─> Asignar especialidades

2. Gestión de agendas
   └─> Configurar horarios por médico
   └─> Ajustar disponibilidades

3. Reportes y análisis
   └─> Agrupar turnos por médico
   └─> Agrupar por especialidad
   └─> Analizar ausencias
   └─> Revisar estadísticas

4. Mantenimiento
   └─> Archivar médicos inactivos
   └─> Actualizar prácticas
   └─> Gestionar permisos de usuarios
```

---

**Este archivo complementa:**

- [README.md](README.md) - Documentación general
- [ESTRUCTURA.md](ESTRUCTURA.md) - Estructura del módulo
- [ELEMENTOS_XML.md](ELEMENTOS_XML.md) - Análisis de elementos XML
- [INSTALACION.md](INSTALACION.md) - Guía de instalación y pruebas
