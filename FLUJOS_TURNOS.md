# 📋 Flujos de Agendado de Turnos

## 🎯 Principio Fundamental

**❗ REGLA CLAVE: El sistema NUNCA permite seleccionar horarios que luego fallen.**

El usuario solo ve y elige entre opciones REALMENTE disponibles.

---

## 🔄 Dos Flujos que Convergen

### 🩺 FLUJO 1: El paciente conoce al médico

**Secuencia paso a paso:**

1. **Buscar Médico**
   - Campo de búsqueda por nombre
   - No se listan todos, solo coincidencias
   - Widget: `<field name="doctor_id" placeholder="Buscar médico..."/>`

2. **Autocompletar Especialidades**
   - El sistema muestra las especialidades del médico seleccionado
   - Si tiene solo 1 → se selecciona automáticamente
   - Si tiene múltiples → el usuario elige
   - Lógica: `@api.onchange('doctor_id')`

3. **Seleccionar Especialidad/Profesión**
   - Ejemplo: "Cirujano" o "Médico Clínico"
   - Dominio dinámico: solo especialidades del médico
   - `domain="[('id', 'in', doctor_id.specialty_ids.ids)]"`

4. **Seleccionar Práctica**
   - Filtrada por la especialidad elegida
   - Ejemplo: "Cirugía General" o "Consulta Clínica"
   - Auto-completa duración

5. **Ver Disponibilidad Real**
   - Sistema calcula slots disponibles con `get_available_slots()`
   - Considera:
     - ✅ Días que trabaja en ESA especialidad
     - ✅ Horarios declarados para ESA especialidad
     - ✅ Turnos no ocupados
     - ✅ Sin bloqueos
   - Ejemplo: Si es cirujano lunes/martes 8-14h → solo muestra esos slots

6. **Seleccionar Horario**
   - Solo aparecen horarios válidos
   - No hay errores posteriores
   - Usuario elige, no prueba

---

### 🏥 FLUJO 2: El paciente NO conoce al médico

**Secuencia paso a paso:**

1. **Seleccionar Especialidad**
   - Ejemplo: "Cardiología", "Pediatría"
   - Widget: `<field name="specialty_id"/>`

2. **Seleccionar Práctica**
   - Filtrada por especialidad
   - Ejemplo: "Electrocardiograma", "Consulta Pediátrica"

3. **Listar Médicos Disponibles**
   - Sistema muestra médicos que tienen esa especialidad
   - Dominio: `[('specialty_ids', 'in', [specialty_id])]`
   - Usuario selecciona uno

4. **Ver Disponibilidad Real**
   - **A partir de aquí, es IDÉNTICO al Flujo 1**
   - Mismo método `get_available_slots()`
   - Mismas validaciones
   - Misma visualización

---

## ⚙️ Implementación Técnica

### 📝 Modelo: `medical.appointment`

**Método Crítico:**
```python
@api.model
def get_available_slots(self, doctor_id, specialty_id, practice_id, year, month):
    """
    Retorna SOLO horarios disponibles.
    
    Entrada:
    - doctor_id: Médico seleccionado
    - specialty_id: Especialidad seleccionada (CRÍTICO)
    - practice_id: Práctica seleccionada
    - year, month: Mes a consultar
    
    Salida:
    {
        'days': {
            '2026-02-10': {
                'day': 10,
                'weekday': 'Lun',
                'slots': [
                    {'time': '08:00', 'datetime': '2026-02-10 08:00:00'},
                    {'time': '09:00', 'datetime': '2026-02-10 09:00:00'},
                ],
                'has_availability': True
            },
            '2026-02-11': { ... }
        }
    }
    
    Validaciones:
    1. Agenda activa del médico
    2. Líneas de horario (schedule_lines) para cada día
    3. Bloqueos (schedule_blocks) - vacaciones, ausencias
    4. Turnos existentes (no solapar)
    5. Duración de la práctica (slots válidos)
    6. No incluir horarios pasados
    """
```

**Métodos onchange:**

```python
@api.onchange('doctor_id')
def _onchange_doctor_id(self):
    """FLUJO 1: Auto-completar especialidades del médico"""
    if self.doctor_id:
        if len(self.doctor_id.specialty_ids) == 1:
            self.specialty_id = self.doctor_id.specialty_ids[0]

@api.onchange('specialty_id')
def _onchange_specialty_id(self):
    """Limpiar práctica si no corresponde a nueva especialidad"""
    if self.practice_id.specialty_id != self.specialty_id:
        self.practice_id = False
    # Si hay médico y no tiene esta especialidad → limpiarlo (Flujo 2)
    if self.doctor_id and self.specialty_id not in self.doctor_id.specialty_ids:
        self.doctor_id = False

@api.onchange('practice_id')
def _onchange_practice_id(self):
    """Auto-completar duración y validar médico"""
    if self.practice_id:
        self.duration = self.practice_id.duration
        if self.doctor_id and self.specialty_id not in self.doctor_id.specialty_ids:
            self.doctor_id = False
```

---

### 🖥️ Vista: Formulario Progresivo

**Estructura:**

```xml
<!-- Paso 1: Elección de entrada -->
<group>
    <group string="FLUJO 1: ¿Conoce al médico?">
        <field name="doctor_id" placeholder="Buscar..."/>
    </group>
    <group string="FLUJO 2: O seleccione especialidad">
        <field name="specialty_id"/>
    </group>
</group>

<!-- Paso 2: Especialidad (si viene por Flujo 1) -->
<group invisible="not doctor_id">
    <field name="specialty_id" 
           domain="[('id', 'in', doctor_id.specialty_ids.ids)]"/>
</group>

<!-- Paso 3: Práctica -->
<group invisible="not specialty_id">
    <field name="practice_id" 
           domain="[('specialty_id', '=', specialty_id)]"/>
</group>

<!-- Paso 4: Médico (si viene por Flujo 2) -->
<group invisible="doctor_id or not specialty_id">
    <field name="doctor_id" 
           domain="[('specialty_ids', 'in', [specialty_id])]"/>
</group>

<!-- Paso 5: CONVERGENCIA - Selección de horario -->
<group invisible="not doctor_id or not specialty_id or not practice_id">
    <div class="alert alert-warning">
        ⚠️ Solo se muestran horarios REALMENTE disponibles
    </div>
    <field name="date_start"/>
</group>
```

---

## 🗓️ Widget de Calendario (Pendiente - Desarrollo JavaScript)

**Funcionalidad Requerida:**

### Vista Mensual
```
    Febrero 2026
< [Lun] [Mar] [Mié] [Jue] [Vie] [Sáb] [Dom] >

     1    2    3    4    5    6    7
     8    9   [10]  11   12   13   14
    15   16   17   18   19   20   21
    22   23   24   25   26   27   28
```

**Características:**
- Días sin disponibilidad: grisados, no clickeables
- Días con disponibilidad: resaltados, clickeables
- Al hacer clic → despliega horarios disponibles
- Navegación: < Mes Anterior | Mes Actual | Mes Siguiente >

### Selección de Horario

Al hacer clic en un día disponible (ej: 10):

```
📅 Lunes 10 de Febrero, 2026

Horarios disponibles:

[ ] 08:00 - 09:00
[ ] 09:00 - 10:00
[ ] 10:00 - 11:00
[ ] 14:00 - 15:00
[ ] 15:00 - 16:00

[Seleccionar]
```

**Reglas:**
- Solo se muestran slots dentro de rangos declarados
- Si no trabaja 12-14h → esos horarios NO aparecen
- Si ya hay turno → ese slot NO aparece
- Usuario elige, sistema valida previamente

---

## 📊 Ejemplo Completo

### Caso: Dr. Martínez

**Especialidades:**
- Cirujano General
- Médico Clínico

**Agenda:**

| Día         | Especialidad      | Horario       |
|-------------|-------------------|---------------|
| Lunes       | Cirujano          | 08:00 - 14:00 |
| Martes      | Cirujano          | 08:00 - 14:00 |
| Miércoles   | Médico Clínico    | 09:00 - 13:00 |
| Jueves      | Médico Clínico    | 09:00 - 13:00 |
| Viernes     | Médico Clínico    | 09:00 - 13:00 |

**Flujo 1 - Paciente busca "Martínez":**
1. Busca "Martínez" → Sistema muestra: Dr. Juan Martínez
2. Selecciona al médico → Sistema carga sus 2 especialidades
3. Elige "Médico Clínico"
4. Elige práctica: "Consulta General" (30 min)
5. Sistema muestra calendario:
   - ❌ Lunes 10 Feb - NO disponible (ese día es cirujano)
   - ❌ Martes 11 Feb - NO disponible (ese día es cirujano)
   - ✅ Miércoles 12 Feb - Disponible: 09:00, 09:30, 10:00, 10:30...
   - ✅ Jueves 13 Feb - Disponible
   - ✅ Viernes 14 Feb - Disponible
6. Selecciona "Miércoles 12, 10:00" → Turno agendado

**Flujo 2 - Paciente sin conocer médico:**
1. Selecciona "Médico Clínico"
2. Selecciona "Consulta General"
3. Sistema lista médicos: Dr. Martínez, Dra. González...
4. Selecciona Dr. Martínez
5. **Desde aquí, idéntico al paso 5 del Flujo 1**

---

## ✅ Estado Actual de Implementación

### Completado ✅
- [x] Modelo con onchange para ambos flujos
- [x] Método `get_available_slots()` con validación completa
- [x] Vista progresiva con campos condicionales
- [x] Dominios dinámicos según selección
- [x] Validación de disponibilidad antes de mostrar
- [x] Detección de solapamientos
- [x] Consideración de bloqueos
- [x] Filtrado por especialidad del médico

### Pendiente ⏳
- [ ] Widget JavaScript para calendario visual
- [ ] Renderizado de slots por día
- [ ] Navegación entre meses
- [ ] Integración con el formulario
- [ ] UX/UI optimizada para selección

---

## 🎯 Beneficios del Diseño

1. **Sin Errores Posteriores**
   - Usuario no puede elegir horarios inválidos
   - Validación preventiva, no reactiva

2. **Transparencia**
   - Usuario ve exactamente qué está disponible
   - No hay sorpresas ni rechazos

3. **Flexibilidad**
   - Dos flujos según conocimiento del paciente
   - Ambos convergen en la misma experiencia

4. **Escalabilidad**
   - Médicos con múltiples especialidades
   - Agendas complejas
   - Fácil agregar nuevas validaciones

5. **Profesional**
   - Como sistemas médicos serios
   - Confianza del usuario
   - Eficiencia operativa

---

**Desarrollado para Odoo v18**  
**Módulo:** medical_appointments  
**Fecha:** Febrero 2026
