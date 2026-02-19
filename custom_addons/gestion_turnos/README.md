# Módulo de Gestión de Turnos Médicos

## Descripción

Este módulo complementa el módulo `medical_management` y proporciona un sistema completo de gestión de turnos médicos con generación automática de slots basada en agendas.

## Características Principales

### 1. Generación Automática de Slots
- Los slots se generan automáticamente basándose en:
  - Las agendas médicas (días y rangos horarios)
  - La duración definida para cada especialidad del médico
  - Se generan on-demand para cualquier fecha solicitada

### 2. Flujo de Solicitud de Turno (Wizard)

El sistema cuenta con un wizard paso a paso para solicitar turnos:

#### Paso 1: Seleccionar Especialidad
- El usuario busca y selecciona la especialidad médica requerida

#### Paso 2: Seleccionar Médico
- Se listan automáticamente solo los médicos que atienden la especialidad seleccionada
- Muestra la cantidad de médicos disponibles

#### Paso 3: Seleccionar Fecha y Horario
- Define un rango de fechas para buscar disponibilidad
- Visualiza los slots disponibles
- Opción de ver slots en calendario
- Los slots se generan automáticamente si no existen

#### Paso 4: Seleccionar Paciente
- Permite elegir entre paciente humano o mascota
- Opción de crear/editar pacientes directamente desde el wizard
- Agregar notas adicionales al turno

### 3. Modelos Principales

#### Appointment Slot (appointment.slot)
- Representa un horario disponible para turnos
- Estados: Disponible, Reservado, Cancelado
- Generación automática basada en agendas
- Relación con médico, especialidad y agenda

#### Medical Appointment (medical.appointment)
- Representa un turno médico confirmado
- Vinculado a un slot específico
- Estados: Agendado, Confirmado, En Curso, Completado, Cancelado, No Asistió
- Control de pago
- Seguimiento con actividades y mensajes

### 4. Vistas Disponibles

#### Slots
- Vista Calendar: Visualización en calendario de slots disponibles
- Vista List: Listado con filtros por estado, médico, especialidad
- Vista Form: Detalles del slot con opciones de liberar/cancelar

#### Turnos
- Vista Calendar: Visualización en calendario de todos los turnos
- Vista Kanban: Organización por estado de turno
- Vista List: Listado completo con filtros avanzados
- Vista Form: Gestión completa del turno con acciones de workflow

### 5. Menús

Bajo "Gestión Médica > Turnos":
- **Solicitar Turno**: Abre el wizard de solicitud
- **Ver Turnos**: Lista y gestión de turnos existentes
- **Slots Disponibles**: Visualización de slots generados

## Instalación

El módulo se instala automáticamente al instalar `medical_management` debido a la configuración `auto_install: True`.

## Dependencias

- `medical_management`: Módulo base con médicos, especialidades, pacientes y agendas

## Uso

### Para solicitar un turno:
1. Ir a "Gestión Médica > Turnos > Solicitar Turno"
2. Seguir el wizard paso a paso
3. Confirmar el turno al finalizar

### Para ver slots disponibles:
1. Ir a "Gestión Médica > Turnos > Slots Disponibles"
2. Filtrar por especialidad, médico o fecha
3. Ver en calendario o lista

### Para gestionar turnos:
1. Ir a "Gestión Médica > Turnos > Ver Turnos"
2. Usar las vistas Calendar/Kanban/List según preferencia
3. Aplicar filtros por estado, médico, fecha, etc.

## Generación de Slots

Los slots se generan automáticamente cuando:
- Un usuario solicita un turno para una fecha específica
- Se buscan slots disponibles para una especialidad/médico
- El sistema verifica agendas activas y genera slots según:
  - Días de atención configurados
  - Rangos horarios de la agenda
  - Duración de turno definida para la especialidad

## Notas Técnicas

- La duración del turno se obtiene de la relación médico-especialidad
- Los slots se almacenan en la base de datos para optimizar rendimiento
- No se duplican slots existentes
- Al cancelar un turno, el slot se libera automáticamente
- Los slots tienen constraint único por médico-fecha-hora

## Próximas Mejoras

- Integración completa con FullCalendar.io para una vista más profesional
- Notificaciones automáticas por email/SMS
- Recordatorios de turnos
- Sistema de confirmación automática
- Gestión de listas de espera

## Soporte

Para consultas o issues, contactar al equipo de desarrollo.
