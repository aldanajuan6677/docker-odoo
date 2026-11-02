# AI_LOG — shop_integration_api & fleet_inspection

## Herramientas
- Gemini (Asistente de desarrollo)

## Prompts clave (3 a 5)
1. ¿Cómo estructuro el enrutamiento HTTP y las validaciones de error (como HTTP 400) en un controlador de Odoo para el Tramo A?
- Me devolvió un ejemplo de estructura con `@http.route` y manejo de excepciones. Tomé la base conceptual adaptándola a la lógica interna de negocio de mis módulos.
2. ¿Cuáles son los pasos detallados para configurar la versión de Odoo mediante el archivo .env según las reglas del proyecto?
- Me indicó cómo declarar `ODOO_VERSION=17.0` en el `.env` y actualizar el README. Verifiqué la compatibilidad con el CLI de Docker de Binaural y apliqué la configuración.
3. ¿Cómo soluciono el error de espacio al intentar compilar el entorno en GitHub Codespaces?
- Me sugirió descartar Codespaces por límites de disco y migrar las pruebas hacia un entorno con recursos adecuados o utilizar Postman de forma remota/alternativa, guiando la estrategia general de despliegue.
4. ¿Cuál es el reemplazo exacto en Odoo 17 para la sintaxis obsoleta de attrs en vistas XML y name_get() en Python para el módulo fleet_inspection?
- Me proporcionó la guía de refactorización hacia atributos directos (`invisible`, `readonly`, `required`) y el uso de `_compute_display_name`. Analicé los cambios y los integré de manera limpia en los archivos del módulo.

## Lo que la IA hizo mal
- La IA sugirió inicialmente flujos de pruebas locales que requerían recursos de hardware muy elevados que mi equipo personal no soportaba por restricciones de espacio en disco.
- Me di cuenta al revisar los logs de error de Docker (`no space left on device`) y evaluar las limitaciones físicas de mi laptop de desarrollo local.

## Lo que escribiste tú sin IA
- La implementación final de la lógica de negocio, consultas ORM y validaciones personalizadas dentro de los modelos de Odoo.
- La ejecución de la estrategia de migración técnica de Odoo 16 a Odoo 17 para el módulo `fleet_inspection` (manifiesto, modelos, vistas y pruebas unitarias).
- La decisión de reestructurar el flujo de pruebas hacia el entorno de la oficina (Binaural) y el control de versiones de los commits con Git.