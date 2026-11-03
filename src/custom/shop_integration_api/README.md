# Shop Integration API

Módulo personalizado desarrollado para Odoo 17 orientado a la integración bidireccional con una tiendas en línea.

## Tramos Completados
- **Tramo A:** Endpoint GET `/api/v1/products` protegido por autenticación de usuario (`auth='user'`) con soporte para filtros avanzados (`category`, `with_stock`, `modified_since`) y manejo robusto de errores con códigos HTTP claros (400).
- **Tramo B:** Endpoint POST `/api/v1/orders` con autenticación segura mediante API Keys nativas de Odoo (`res.users.apikeys`) a través de la cabecera `Authorization: Bearer`[cite: 5]. Validación estricta de negocio (existencia de RIF de cliente, productos por código `default_code`, cantidades válidas) respondiendo con formato JSON estandarizado y código HTTP **422** en caso de fallos[cite: 2, 5]. Incorpora un modelo de auditoría de llamadas (`shop.api.log`) que registra endpoints, usuarios, duraciones y códigos de respuesta **sin almacenar jamás credenciales ni tokens**[cite: 5].

## Supuestos de Diseño
1. **Estado del Pedido:** Los pedidos de venta creados a través de la API nacen con estado de borrador (cotizaciones) para garantizar una revisión y validación previa por parte del equipo comercial antes de ser confirmados[cite: 5].
2. **Autenticación por API Key:** Se utiliza el modelo nativo de Odoo (`res.users.apikeys`), lo que permite que cada integración externa disponga de una clave segura revocable por usuario sin exponer contraseñas de acceso[cite: 5].

## Cómo Probarlo
Puedes ejecutar la suite de pruebas unitarias y de integración automatizadas mediante el comando estándar de Odoo:

\`\`\`bash
./odoo test -d prueba_limpia -m shop_integration_api
\`\`\`