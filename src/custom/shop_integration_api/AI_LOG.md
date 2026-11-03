# AI_LOG — shop_integration_api

## Herramientas
- Gemini (Asistente de desarrollo)

## Prompts
1. ¿Cómo estructuro el enrutamiento HTTP y las validaciones de error (como HTTP 400 en un controlador de Odoo?
- Me devolvió un ejemplo de estructura con `@http.route` y manejo de excepciones. Tomé la base conceptual adaptándola a la lógica interna de negocio del módulo.

-¿Cuál es el método nativo en Odoo 17 para validar las API keys de res.users.apikeys y cómo estructurar el manejo de errores HTTP 422 para peticiones POST de creación de pedidos?
- Me proporcionó la implementación del método `_check_credentials` para autenticación con cabecera Bearer y el formato JSON estandarizado para errores de validación de negocio. Integré y ajusté los bloques en los controladores correspondientes.