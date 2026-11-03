# Reporte de Incidente — T-200

## 1. Cómo se reproduce
1. Iniciar sesión en el sistema Odoo utilizando las credenciales de un usuario asignado al grupo de **Vendedor** (`sales_team.group_sale_salesman`).
2. Crear un nuevo presupuesto de venta (`sale.order`) y añadir al menos una línea de producto.
3. Hacer clic en el botón **"Confirmar pedido"** (`action_confirm`).
4. **Resultado obtenido:** El sistema interrumpe la ejecución y muestra una advertencia en rojo por un error de permisos (`AccessError`), impidiendo completar la venta.

## 2. Causa Raíz
Tras el despliegue de la última actualización, se introdujo la lógica para evaluar las reglas de comisión por categoría (`sale.commission.rule`) al confirmar las líneas del pedido. Sin embargo, en el archivo de control de acceso (`security/ir.model.access.csv`), se omitió declarar el permiso de lectura (`read`) para el rol de los vendedores sobre el modelo `sale.commission.rule`. Dado que los gerentes poseen permisos administrativos totales, el error no se manifestaba al operar con cuentas de gerencia.

## 3. Corrección Aplicada
Se aplicó el cambio mínimo requerido en el archivo `security/ir.model.access.csv`, añadiendo la regla de acceso para otorgar permisos exclusivos de consulta (`read=1, write=0, create=0, unlink=0`) al grupo `sales_team.group_sale_salesman` sobre el modelo `model_sale_commission_rule`, evitando sobreasignar privilegios innecesarios.

## 4. Prueba de Validación
Se implementó una prueba unitaria automatizada (`TestSaleCommissionHotfix`) configurada para ejecutarse en el contexto de un usuario con rol estrictamente de vendedor (`with_user(self.salesman)`), la cual simula la creación y confirmación de un pedido de venta, validando que el flujo concluya de manera exitosa y que las comisiones se calculen correctamente.