# Solicitudes de Pago con Aprobación (payment_request)

Módulo para la gestión y control de solicitudes de pago a proveedores adaptado a los requerimientos de la prueba técnica.

## Tramos Completados
- **Tramo A:** Modelo base `payment.request` con integración de `mail.thread`, secuencia automática (`SP/2026/0001`), gestión de estados (borrador, enviada, aprobada, pagada, rechazada), definición de grupos de seguridad (Solicitante, Aprobador, Tesorería), reglas de registro para restringir la vista a los propios documentos del solicitante, vistas de lista, formulario, búsqueda y pruebas unitarias/integración[cite: 6].

## Supuestos y Preguntas al Cliente 
1. **Pregunta a Carolina (Gerente de Administración):** ¿Qué define un "pago normal" (aprobado por el jefe de área) frente a un "pago grande" (aprobado por gerencia)?
   - *Supuesto asumido para avanzar:* En el Tramo A se implementa un modelo de aprobación unificado por roles; los niveles de monto específicos se configuran de manera escalable en otro tramo.
2. **Pregunta a Carolina:** ¿Los pagos en bolívares de facturas en dólares se calculan a la tasa oficial BCV del día de la emisión o del día del pago?
   - *Supuesto asumido para avanzar:* Se maneja la moneda predeterminada de la compañía en el Tramo A, dejando la conversión multimoneda y tasa de cambio oficial para otro tramo.

## Cómo Probarlo
Ejecuta las pruebas automatizadas con el comando:
\`\`\`bash
./odoo test -d prueba_limpia -m payment_request
\`\`\`