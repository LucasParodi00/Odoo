# Instrucciones para Actualizar el Módulo

## Cambios Realizados

Se han corregido los problemas con la visualización de horarios disponibles en el módulo `medical_appointments`. Los cambios principales son:

### 1. Corrección en `_generate_slots_html`
- **Problema**: Los horarios no se mostraban al hacer clic en un día disponible
- **Solución**: 
  - Se reescribió completamente la generación de HTML
  - Se agregó un overlay oscuro de fondo para mejor UX
  - Los popups ahora se generan fuera del grid del calendario
  - Se mejoró el sistema de IDs únicos para evitar conflictos
  - Se agregaron mensajes de debug para facilitar diagnóstico

### 2. Mejoras adicionales
- IDs únicos con scope del contenedor
- Mejor manejo de eventos de cierre (clic en overlay o botón)
- CSS con scope específico para evitar conflictos globales
- Validación de datos de slots con mensajes de error descriptivos

## Cómo Actualizar el Módulo en Odoo

### Opción 1: Desde la interfaz web (Recomendado)

1. Ir a **Aplicaciones** en el menú principal
2. Buscar "Gestión de Turnos Médicos"
3. Click en los 3 puntos (⋮) del módulo
4. Seleccionar **"Actualizar"**
5. Confirmar la actualización

### Opción 2: Desde línea de comandos

```powershell
# Navegar al directorio de Odoo
cd D:\Odoo\odoo18

# Actualizar el módulo (reemplazar 'su_database' con el nombre de su base de datos)
python odoo-bin -c odoo.conf -d su_database -u medical_appointments --stop-after-init
```

### Opción 3: Reiniciar servicio (si está instalado como servicio)

```powershell
# Reiniciar el servicio de Odoo
Restart-Service -Name "OdooService"
```

## Verificación del Funcionamiento

Después de actualizar:

1. Ir a **Turnos Médicos** → **Crear nuevo turno**
2. Seleccionar:
   - **Médico** o **Especialidad** (según el flujo preferido)
   - **Especialidad** o **Médico** (completar la selección)
   - **Práctica/Atención**
3. **Verificar el calendario de disponibilidad**:
   - Los días VERDES deben mostrar "✓ X turnos"
   - Al hacer clic en un día verde, debe aparecer un popup con overlay oscuro
   - El popup debe mostrar todos los horarios disponibles
   - Al hacer clic en un horario, debe seleccionarse automáticamente
   - El popup debe cerrarse al seleccionar un horario o hacer clic en "Cerrar" o en el overlay

## Troubleshooting

### Los horarios aún no aparecen

1. **Limpiar caché del navegador** (Ctrl + Shift + Delete)
2. **Recargar con Ctrl + F5** (recarga forzada)
3. **Verificar en modo incógnito**

### Los días verdes no aparecen

1. Verificar que el médico tenga una **agenda activa** para la especialidad seleccionada
2. Verificar que la agenda tenga **líneas de horario** configuradas
3. Verificar que no haya **bloqueos** en las fechas

### El popup aparece vacío

- Si aparece el mensaje "⚠️ Error: Día con X slots pero no se generó HTML", contactar soporte técnico
- Esto indicaría un problema en la estructura de datos de los slots

## Soporte

Si después de actualizar el módulo persisten los problemas:

1. Revisar los logs de Odoo en modo debug
2. Verificar la consola del navegador (F12) en busca de errores JavaScript
3. Asegurarse de que todos los campos requeridos estén completos en la agenda médica

---

**Fecha de actualización**: 3 de febrero de 2026  
**Versión del módulo**: 18.0.1.0.0  
**Archivos modificados**: `models/medical_appointment.py`
