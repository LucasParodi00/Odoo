# Gestión Médica - Odoo 18

## Descripción

Sistema completo de gestión médica para centros de salud orientado a una sola sucursal.

## Características Implementadas

### ✅ Especialidades Médicas

- Gestión completa de especialidades
- Campos: nombre, código, color y estado activo
- Validación de códigos únicos
- Vista de lista con filtros
- Selector de colores para identificación visual

### ✅ Médicos

- Integración con módulo de Contactos
- Campo "Es Médico" en contactos
- Número de matrícula (único por médico)
- DNI/CUIL del profesional
- Asignación de especialidades (una o múltiples)
- Vistas especializadas: kanban, lista y formulario
- Validación de matrícula única
- Filtros y agrupación por especialidad

## Próximas Características

### 🔄 En Desarrollo

- Grid principal de turnos
- Gestión de médicos
- Gestión de pacientes
- Sistema de agendas
- Gestión de turnos/citas

## Instalación

1. Copiar el módulo en la carpeta `custom_addons`
2. Actualizar la lista de aplicaciones
3. Buscar "Gestión Médica" e instalar

## Uso

### Especialidades

1. Ir a **Gestión Médica > Configuración > Especialidades**
2. Crear nuevas especialidades con:
   - Nombre descriptivo (ej: Consulta Oftalmológica)
   - Código corto (ej: co, of, cg)
   - Color para identificación
   - Estado activo/inactivo

### Médicos

1. Ir a **Gestión Médica > Médicos**
2. Crear nuevo médico con:
   - Datos del contacto (nombre, teléfono, email)
   - Número de matrícula profesional (obligatorio)
   - DNI o CUIL
   - Una o más especialidades
3. También puede marcar como médico a un contacto existente desde **Contactos**
4. Los médicos se pueden visualizar en tres formatos:
   - **Kanban**: Vista de tarjetas con información resumida
   - **Lista**: Tabla con todos los datos
   - **Formulario**: Detalle completo del médico

## Requisitos

- Odoo 18.0
- Módulos base: base, mail, calendar

## Autor

Tu Empresa

## Licencia

LGPL-3
