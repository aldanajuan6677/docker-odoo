# AI_LOG — payment_request

## Herramientas
- Gemini (Asistente de desarrollo)

## Prompts clave
1. ¿Cómo estructurar correctamente una regla de registro (`ir.rule`) en Odoo para que los usuarios del grupo Solicitante solo puedan visualizar sus propios registros creados?
- Se diseñó el dominio `[('create_uid', '=', user.id)]` aplicado al grupo correspondiente.