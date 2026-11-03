## Herramientas
- Gemini (Asistente de desarrollo)

## Prompts clave (3 a 5)
1. ¿Cómo estructuro la corrección de permisos en ir.model.access.csv y el diseño de la prueba unitaria para un rol de vendedor sin sobreasignar privilegios ?
- Consulté las pautas para aislar el contexto del usuario vendedor (`with_user`) y el permiso exacto de solo lectura en el modelo de reglas de comisión. Validé y ajusté los cambios para solucionar la causa raíz de forma mínima y segura.

## Lo que la IA hizo mal
- Ninguna desviación relevante; la propuesta de solución se ajustó estrictamente al principio de cambio mínimo requerido por el ticket.

## Lo que escribiste tú sin IA
- La aplicación del parche de seguridad estricto en el control de acceso y la documentación detallada del incidente en el archivo `INCIDENT.md`.