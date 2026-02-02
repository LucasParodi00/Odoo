# Gestión de Turnos Médicos

## Descripción

Módulo completo de gestión de turnos médicos para Odoo v18, diseñado para ser genérico y escalable, apto tanto para clínicas médicas como veterinarias.

## Características Principales

### 🎯 Especialidades Médicas

- Punto de inicio obligatorio del flujo de turnos
- Configurables para pacientes personas, animales o ambos
- Especialidades predefinidas (medicina general, pediatría, veterinaria, etc.)

### 👨‍⚕️ Médicos

- Vinculados a contactos (res.partner)
- Múltiples especialidades por médico
- Agenda configurable con horarios y bloqueos

### 📅 Agenda Médica

- Configuración de días y rangos horarios
- Múltiples rangos por día
- Bloqueos de agenda (vacaciones, ausencias, capacitaciones)
- Validación automática de disponibilidad

### 🔄 Flujos de Solicitud de Turnos

#### Flujo A - Con Preferencia de Médico

1. Selección de especialidad
2. Selección de médico específico
3. Visualización de disponibilidad
4. Selección de fecha y hora
5. Confirmación del turno

#### Flujo B - Sin Preferencia de Médico

1. Selección de especialidad
2. Selección de fecha deseada
3. Sistema muestra médicos disponibles
4. Selección de médico
5. Confirmación del turno

### 🩺 Prácticas/Atenciones

- Definición de tipos de atención por especialidad
- Duración configurable (para cálculo automático de horarios)
- Prácticas predefinidas (consultas, cirugías, tratamientos)

### 📆 Turnos

- Estados: borrador, confirmado, atendido, cancelado, ausente
- Validaciones automáticas de disponibilidad
- Cálculo automático de hora de fin según duración
- Vista calendario integrada
- Acciones: confirmar, atender, cancelar, reprogramar

### 👤 Pacientes

#### Personas

- Uso del módulo estándar de Contactos
- Creación desde flujo de turnos
- Historial de turnos y consultas

#### Animales

- Entidad propia para mascotas
- Vinculados a dueño/tutor
- Información específica: especie, raza, edad, peso, microchip
- Historial médico veterinario

### 📋 Historia Clínica

- Creación automática al atender turno
- Campos: síntomas, examen físico, diagnóstico, tratamiento
- Signos vitales opcionales
- Adjuntos (estudios, radiografías, análisis)
- Vinculada a paciente, médico y turno

## Elementos XML Utilizados

### Modelos (Models)

- `medical.specialty` - Especialidades médicas
- `medical.practice` - Prácticas/atenciones
- `medical.doctor` - Médicos
- `medical.schedule` - Agendas
- `medical.schedule.line` - Líneas de agenda (horarios)
- `medical.schedule.block` - Bloqueos
- `medical.appointment` - Turnos
- `medical.patient.animal` - Pacientes animales
- `medical.clinical.history` - Historias clínicas
- `res.partner` - Extensión para pacientes

### Vistas (Views)

- **Tree** - Listas tabulares
- **Form** - Formularios de edición
- **Kanban** - Vistas de tarjetas
- **Calendar** - Calendarios interactivos
- **Search** - Filtros y búsquedas

### Elementos de Interfaz

- **Widgets**:
  - `statusbar` - Barra de estados
  - `many2many_tags` - Tags de relaciones múltiples
  - `boolean_toggle` - Interruptor booleano
  - `statinfo` - Botones estadísticos
  - `float_time` - Entrada de tiempo
  - `color_picker` - Selector de colores
  - `image` - Visualizador de imágenes
  - `badge` - Etiquetas de estado

- **Botones inteligentes (Smart Buttons)**: Contadores con acciones
- **Ribbon**: Cintas de estado (archivado, inactivo)
- **Chatter**: Sistema de mensajería y actividades
- **Notebook/Pages**: Pestañas organizadoras

### Seguridad

- Grupos de acceso:
  - Usuario médico
  - Recepcionista
  - Médico
  - Administrador
- Control granular de permisos (CRUD) por grupo
- Archivo `ir.model.access.csv` para permisos

### Datos

- **Data**: Datos iniciales (especialidades, prácticas)
- **Demo**: Datos de demostración (médicos, pacientes, agendas)
- Uso de `noupdate="1"` para datos de referencia

### Menús

- Menú raíz con icono personalizado
- Submenús organizados por funcionalidad:
  - Turnos
  - Pacientes
  - Historias Clínicas
  - Médicos
  - Configuración

## Arquitectura Técnica

### Herencia

- `mail.thread` - Sistema de mensajería
- `mail.activity.mixin` - Gestión de actividades

### Validaciones

- `@api.constrains` - Validaciones de integridad
- Verificación de disponibilidad médica
- Control de solapamientos
- Validación de bloqueos de agenda

### Campos Computados

- Cálculo automático de duración
- Nombres compuestos dinámicos
- Contadores de relaciones
- Estados derivados

### Acciones

- Confirmación de turnos
- Atención y creación automática de HC
- Cancelación con motivo
- Reprogramación
- Marcado de ausencias

## Instalación

1. Copiar el módulo a la carpeta `addons` o `custom_addons`
2. Actualizar lista de aplicaciones
3. Instalar "Gestión de Turnos Médicos"

## Dependencias

- `base` - Módulo base de Odoo
- `contacts` - Gestión de contactos
- `calendar` - Funcionalidad de calendario
- `mail` - Sistema de mensajería

## Configuración Inicial

1. Configurar especialidades médicas (o usar las predefinidas)
2. Registrar médicos con sus especialidades
3. Configurar agendas médicas (días y horarios)
4. Definir prácticas/atenciones por especialidad
5. ¡Comenzar a gestionar turnos!

## Escalabilidad Futura

El diseño modular permite agregar:

- Consultorios físicos
- Integración con facturación
- Portal de pacientes para autogestión
- Recordatorios automáticos (email/SMS)
- Reportes y estadísticas
- Telemedicina
- Recetas electrónicas
- Gestión de stock de insumos médicos

## Licencia

LGPL-3

## Autor

Odoo Medical Team

## Versión

18.0.1.0.0
