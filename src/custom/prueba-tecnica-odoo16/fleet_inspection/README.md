# Inspecciones de vehículos (`fleet_inspection`)

Módulo escrito para **Odoo 16**. Es el punto de partida del **Ejercicio 2 — Migración** de la prueba técnica.

## Qué hace

- Registra inspecciones de los vehículos de Flota con un checklist de puntos (frenos, luces, cauchos…) que se carga solo al crear la inspección.
- Estados: borrador → en curso → aprobada / rechazada. Un punto crítico con falla impide aprobar.
- Tipo de vehículo como campo de selección: moto, carro, camión u otro.
- Grupos: *Inspector* (ve solo sus inspecciones) y *Supervisor de inspecciones* (ve todas, aprueba y rechaza).
- Acción planificada diaria que marca las inspecciones con más de 7 días en curso y le crea una actividad al inspector.
- Reporte PDF de la inspección.

## Cómo probarlo (Odoo 16)

```bash
./odoo test -d prueba_16 -m fleet_inspection
```

## Tabla de Migración — `fleet_inspection` (Odoo 16 a Odoo 17)

| Qué cambió | Por qué | Cómo lo resolviste |
| :--- | :--- | :--- |
| **Versión en Manifiesto** | Adaptación a la versión declarada en el proyecto. | Se actualizó `"version": "17.0.1.0.0"` en `__manifest__.py`. |
| **Sintaxis `attrs={...}` en vistas XML** | El atributo `attrs` fue deprecado en Odoo 17 en favor de expresiones directas. | Se reemplazó `attrs="{'invisible': ...}"`, `attrs="{'readonly': ...}"` y `attrs="{'required': ...}"` por atributos directos `invisible="..."`, `readonly="..."` y `required="..."`. |
| **Atributos `states="..."` en `<button>`** | Los botones de la cabecera en Odoo 17 ya no soportan el atributo `states`. | Se sustituyó `states="..."` por condiciones de invisibilidad directas, ej.: `invisible="state != 'draft'"`. |
| **Definiciones `states={...}` en Python** | Los parámetros `states` definidos en la declaración de campos del ORM de Python fueron retirados en Odoo 17. | Se removió `states={...}` del modelo en Python y se trasladó la condición de de solo lectura (`readonly`) a las vistas XML correspondiente. |
| **Método `name_get()`** | El método `name_get()` fue eliminado en Odoo 17 en favor del sistema de cómputo de `display_name`. | Se reemplazó por la función decorada `@api.depends(...)` denominada `_compute_display_name(self)`. |
