# Análisis de Elementos XML en el Módulo de Gestión de Turnos Médicos

## 1. VISTAS (Views)

### 1.1 Tree Views (Listas)

Representación tabular de registros, ideal para visualización masiva de datos.

**Elementos utilizados:**

- `<tree>` - Contenedor principal
- `<field>` - Columnas de datos
- Atributos de decoración:
  - `decoration-info` - Color azul (turnos en borrador)
  - `decoration-success` - Color verde (turnos atendidos)
  - `decoration-danger` - Color rojo (turnos cancelados)
  - `decoration-warning` - Color naranja (turnos ausentes)
  - `decoration-muted` - Color gris (inactivos)

**Widgets en Tree:**

- `boolean_toggle` - Interruptor on/off visual
- `badge` - Etiqueta de estado con color
- `many2many_tags` - Chips de relaciones múltiples

**Ejemplo:**

```xml
<tree decoration-success="state=='attended'">
    <field name="patient_name"/>
    <field name="state" widget="badge"/>
</tree>
```

### 1.2 Form Views (Formularios)

Vistas de detalle para creación y edición de registros.

**Estructura típica:**

```xml
<form>
    <header>        <!-- Botones de acción y statusbar -->
    <sheet>         <!-- Contenido principal -->
        <div class="oe_button_box"/>  <!-- Smart buttons -->
        <widget name="web_ribbon"/>    <!-- Cinta de estado -->
        <group>                        <!-- Agrupación de campos -->
        <notebook>                     <!-- Pestañas -->
            <page>                     <!-- Contenido por pestaña -->
    <chatter/>      <!-- Sistema de mensajería -->
</form>
```

**Elementos clave:**

**Header:**

- `<button>` - Botones de acción con `type="object"`
- `<field name="state" widget="statusbar">` - Barra de progreso de estados
- Atributo `invisible` - Control de visibilidad condicional

**Smart Buttons (Botones Estadísticos):**

```xml
<button name="%(action_id)d" type="action" class="oe_stat_button" icon="fa-calendar">
    <field name="count" widget="statinfo" string="Label"/>
</button>
```

**Web Ribbon (Cinta):**

```xml
<widget name="web_ribbon" title="Archivado" bg_color="text-bg-danger" invisible="active"/>
```

**Notebook/Pages (Pestañas):**

```xml
<notebook>
    <page string="Título" name="identificador">
        <!-- Contenido -->
    </page>
</notebook>
```

### 1.3 Kanban Views (Tarjetas)

Vista de tarjetas tipo tablero, ideal para visualización visual y agrupación.

**Estructura:**

```xml
<kanban class="o_kanban_mobile" default_group_by="state">
    <field name="campo"/>  <!-- Campos necesarios -->
    <templates>
        <t t-name="card">
            <!-- Diseño de tarjeta con QWeb -->
        </t>
    </templates>
</kanban>
```

**Elementos en tarjeta:**

- `o_kanban_record_has_image_fill` - Contenedor con imagen
- `o_kanban_image` - Área de imagen
- `oe_kanban_details` - Detalles de la tarjeta
- `o_kanban_record_title` - Título principal
- `o_kanban_record_subtitle` - Subtítulo
- `o_kanban_tags_section` - Área de badges
- `badge text-bg-primary/info/success` - Etiquetas de Bootstrap

### 1.4 Calendar Views (Calendarios)

Visualización de eventos en calendario, fundamental para turnos médicos.

**Configuración:**

```xml
<calendar string="Título"
          date_start="campo_inicio"
          date_stop="campo_fin"
          color="campo_color"
          mode="week"              <!-- day/week/month -->
          quick_create="0"         <!-- Desactivar creación rápida -->
          event_open_popup="1">    <!-- Abrir en popup -->
    <field name="campo1"/>
    <field name="campo2" filters="1"/>  <!-- Filtros laterales -->
</calendar>
```

### 1.5 Search Views (Búsquedas y Filtros)

Define filtros, búsquedas y agrupaciones.

**Elementos:**

**Field (Búsqueda por campo):**

```xml
<field name="name"/>  <!-- Búsqueda textual -->
```

**Filter (Filtros predefinidos):**

```xml
<filter string="Activos" name="filter_active" domain="[('active', '=', True)]"/>
```

**Filtros de fecha:**

```xml
<filter string="Hoy" name="filter_today"
        domain="[('date', '&gt;=', context_today())]"/>
```

**Agrupaciones:**

```xml
<group expand="0" string="Agrupar Por">
    <filter string="Estado" name="group_state" context="{'group_by': 'state'}"/>
</group>
```

## 2. WIDGETS (Controles Especiales)

### Widgets en Campos

| Widget             | Uso                    | Ejemplo                   |
| ------------------ | ---------------------- | ------------------------- |
| `boolean_toggle`   | Interruptor visual     | Estado activo/inactivo    |
| `statusbar`        | Barra de estados       | Flujo de turnos           |
| `statinfo`         | Estadística en botón   | Contador de turnos        |
| `many2many_tags`   | Tags múltiples         | Especialidades del médico |
| `float_time`       | Entrada de tiempo      | Duración en horas         |
| `color_picker`     | Selector de color      | Color de identificación   |
| `image`            | Visualizador de imagen | Foto del animal           |
| `badge`            | Etiqueta de estado     | Estado del turno          |
| `phone`            | Enlace telefónico      | Número de contacto        |
| `email`            | Enlace de email        | Correo electrónico        |
| `many2many_binary` | Gestión de archivos    | Adjuntos en HC            |

### Widget Web Ribbon

Cinta decorativa para estados especiales:

```xml
<widget name="web_ribbon" title="Texto" bg_color="text-bg-danger" invisible="condicion"/>
```

Colores disponibles: `text-bg-primary`, `text-bg-success`, `text-bg-danger`, `text-bg-warning`, `text-bg-info`

## 3. ACCIONES (Actions)

### ir.actions.act_window

Define ventanas de acción para abrir vistas.

```xml
<record id="action_medical_appointment" model="ir.actions.act_window">
    <field name="name">Turnos Médicos</field>
    <field name="res_model">medical.appointment</field>
    <field name="view_mode">calendar,tree,kanban,form</field>
    <field name="context">{'search_default_filter_confirmed': 1}</field>
    <field name="domain">[('state', '!=', 'cancelled')]</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Mensaje cuando no hay registros
        </p>
    </field>
</record>
```

**Campos clave:**

- `view_mode` - Orden de vistas disponibles
- `context` - Valores por defecto y filtros pre-aplicados
- `domain` - Filtro de registros
- `help` - Mensaje de ayuda cuando no hay datos

## 4. MENÚS (Menus)

### Menú Principal

```xml
<menuitem id="menu_medical_root"
          name="Gestión Médica"
          web_icon="medical_appointments,static/description/icon.png"
          sequence="50"/>
```

### Submenús

```xml
<menuitem id="menu_medical_appointments"
          name="Turnos"
          parent="menu_medical_root"
          sequence="10"/>
```

### Menú con Acción

```xml
<menuitem id="menu_medical_appointment_all"
          name="Todos los Turnos"
          parent="menu_medical_appointments"
          action="action_medical_appointment"
          sequence="10"/>
```

### Menú con Grupos de Seguridad

```xml
<menuitem id="menu_medical_config"
          name="Configuración"
          parent="menu_medical_root"
          groups="group_medical_manager"/>
```

## 5. SEGURIDAD (Security)

### Grupos de Acceso

```xml
<record id="group_medical_user" model="res.groups">
    <field name="name">Usuario</field>
    <field name="category_id" ref="module_category_medical"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Archivo ir.model.access.csv

Formato: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`

Ejemplo:

```csv
access_medical_appointment_user,medical.appointment.user,model_medical_appointment,group_medical_user,1,0,0,0
```

## 6. DATOS (Data)

### Data (Datos Iniciales)

```xml
<odoo>
    <data noupdate="1">
        <record id="specialty_general" model="medical.specialty">
            <field name="name">Clínica General</field>
            <field name="code">CLG</field>
        </record>
    </data>
</odoo>
```

**noupdate="1"**: No actualizar en upgrade (solo crear)

### Relaciones Many2many

```xml
<field name="specialty_ids" eval="[(6, 0, [ref('specialty_1'), ref('specialty_2')])]"/>
```

Operaciones:

- `(6, 0, [ids])` - Reemplazar con lista de IDs
- `(4, id)` - Agregar ID
- `(3, id)` - Remover ID
- `(5,)` - Limpiar todos

## 7. HERENCIA DE VISTAS

### Extensión de Vista Existente

```xml
<record id="view_partner_form_medical" model="ir.ui.view">
    <field name="name">res.partner.form.medical</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//div[@name='button_box']" position="inside">
            <!-- Contenido a agregar -->
        </xpath>
    </field>
</record>
```

**Posiciones xpath:**

- `inside` - Dentro del elemento
- `after` - Después del elemento
- `before` - Antes del elemento
- `replace` - Reemplazar elemento
- `attributes` - Modificar atributos

## 8. CHATTER (Sistema de Mensajería)

Para modelos con herencia de `mail.thread` y `mail.activity.mixin`:

```xml
<form>
    <sheet>
        <!-- Contenido -->
    </sheet>
    <chatter/>
</form>
```

## 9. ATRIBUTOS ESPECIALES

### Visibilidad Condicional

```xml
<field name="campo" invisible="state != 'draft'"/>
<field name="campo" invisible="patient_type == 'person'"/>
```

### Dominios Dinámicos

```xml
<field name="doctor_id" domain="[('specialty_ids', 'in', [specialty_id])]"/>
```

### Contexto

```xml
<field name="patient_id" context="{'default_is_patient': True}"/>
```

### Opciones

```xml
<field name="specialty_id" options="{'no_create': True, 'no_open': True}"/>
```

### Required, Readonly

```xml
<field name="campo" required="1" readonly="state != 'draft'"/>
```

## 10. CLASES CSS UTILIZADAS

### Odoo Específicas

- `oe_button_box` - Contenedor de smart buttons
- `oe_stat_button` - Botón estadístico
- `oe_title` - Título principal del formulario
- `oe_kanban_global_click` - Toda la tarjeta es clickeable
- `o_kanban_mobile` - Estilo móvil para kanban

### Bootstrap 5 (Odoo 18)

- `text-bg-primary`, `text-bg-success`, etc. - Badges con color
- `badge` - Etiqueta
- `btn`, `btn-primary` - Botones
- `mb-2`, `mt-4` - Márgenes

## Resumen de Elementos XML por Vista

| Vista        | Elementos Principales                                             |
| ------------ | ----------------------------------------------------------------- |
| **Tree**     | field, decoration-\*, widget                                      |
| **Form**     | header, sheet, button_box, ribbon, group, notebook, page, chatter |
| **Kanban**   | templates, t-name, QWeb expressions                               |
| **Calendar** | date_start, date_stop, color, mode                                |
| **Search**   | field, filter, separator, group                                   |

## Conclusión

El módulo utiliza prácticamente todos los elementos XML disponibles en Odoo v18:

- ✅ Vistas: Tree, Form, Kanban, Calendar, Search
- ✅ Widgets: 12+ tipos diferentes
- ✅ Acciones: ir.actions.act_window
- ✅ Menús: Jerárquicos con iconos y seguridad
- ✅ Seguridad: Grupos y permisos granulares
- ✅ Datos: Iniciales y demo con relaciones
- ✅ Herencia: Extensión de vistas existentes
- ✅ Chatter: Sistema de mensajería integrado

Este análisis sirve como referencia completa de los elementos XML utilizados en desarrollo Odoo.
