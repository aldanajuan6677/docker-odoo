import json
import logging
import time
from dateutil.parser import parse

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ShopProductApiController(http.Controller):

    @http.route('/api/v1/products', type='http', auth='user', methods=['GET'], csrf=False)
    def get_products(self, **kwargs):
        """
        Endpoint para consultar productos activos y vendibles con stock y filtros opcionales.
        Filtros soportados en URL:
          - category: ID de la categoría (ej: ?category=3)
          - with_stock: Si es '1' o 'true', devuelve solo productos con stock > 0
          - modified_since: Fecha ISO o legible (ej: ?modified_since=2026-01-01)
        """
        # 1. Dominio base obligatorio (Productos activos y vendibles)
        domain = [
            ('active', '=', True),
            ('sale_ok', '=', True),
        ]

        # 2. Procesar filtro por categoría si fue enviado
        category = kwargs.get('category')
        if category:
            try:
                domain.append(('categ_id', '=', int(category)))
            except ValueError:
                return request.make_json_response(
                    {'error': {'code': 'INVALID_CATEGORY', 'message': 'El parámetro category debe ser un entero válido.'}},
                    status=400
                )

        # 3. Procesar filtro por fecha 'modified_since' con manejo de errores amigable
        modified_since = kwargs.get('modified_since')
        if modified_since:
            try:
                # Intentamos parsear la fecha enviada
                parsed_date = parse(modified_since)
                formatted_date = fields.Datetime.to_string(parsed_date)
                domain.append(('write_date', '>=', formatted_date))
            except (ValueError, TypeError):
                # Si la fecha está mal escrita, devolvemos error 400 claro en lugar de error 500
                return request.make_json_response(
                    {'error': {'code': 'INVALID_DATE_FORMAT', 'message': f"La fecha '{modified_since}' no tiene un formato válido (Ejemplo válido: YYYY-MM-DD)."}},
                    status=400
                )

        # 4. Consultar los productos en Odoo (usamos product.product para obtener variantes y stock real)
        products = request.env['product.product'].search(domain)

        # 5. Filtrar opcionalmente "solo con stock" en memoria
        with_stock = kwargs.get('with_stock', '').lower() in ['1', 'true', 'yes']
        if with_stock:
            products = products.filtered(lambda p: p.qty_available > 0)

        # 6. Mapear datos a devolver en JSON
        product_data = []
        for p in products:
            product_data.append({
                'id': p.id,
                'code': p.default_code or '',
                'name': p.display_name,
                'price': p.list_price,
                'qty_available': p.qty_available,
            })

        # 7. Retornar respuesta exitosa en formato JSON (HTTP 200)
        return request.make_json_response({'products': product_data}, status=200)


class ShopOrderApiController(http.Controller):

    def _authenticate_request(self):
        """
        Valida la cabecera 'Authorization: Bearer <api_key>' utilizando 
        el mecanismo nativo de API Keys de Odoo (res.users.apikeys).
        Retorna el registro del usuario si es válido, o None si falla.
        """
        auth_header = request.httprequest.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        if not token:
            return None

        # Verificar la API key usando el método nativo del modelo res.users.apikeys
        user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=token)
        if not user_id:
            return None

        return request.env["res.users"].browse(user_id)

    def _log_api_call(self, endpoint, user, response_code, start_time):
        """
        Registra cada llamada a la API en el modelo 'shop.api.log'.
        Garantiza que NUNCA se almacene la clave/token de autorización por seguridad[cite: 5].
        """
        duration = time.time() - start_time
        try:
            request.env["shop.api.log"].sudo().create({
                "endpoint": endpoint,
                "user_id": user.id if user else False,
                "response_code": str(response_code),
                "duration": duration,
            })
        except Exception as e:
            _logger.error("No se pudo registrar el log de la API: %s", str(e))

    def _json_error(self, status_code, code, field, message):
        """Construye la respuesta de error estructurada con el formato HTTP 422 requerido[cite: 2, 5]."""
        error_body = {
            "error": {
                "code": code,
                "field": field,
                "message": message,
            }
        }
        return request.make_json_response(
            error_body,
            status=status_code
        )

    @http.route("/api/v1/orders", type="json", auth="none", methods=["POST"], csrf=False)
    def create_order(self, **kw):
        """
        Endpoint POST /api/v1/orders (Tramo B)
        Recibe el RIF del cliente, una referencia externa y las líneas (código de producto y cantidad).
        Crea el pedido de venta en Odoo como cotización (borrador)[cite: 5].
        """
        start_time = time.time()
        endpoint = "/api/v1/orders"

        # 1. Autenticación Bearer (API Key nativa)[cite: 5]
        user = self._authenticate_request()
        if not user:
            self._log_api_call(endpoint, None, 401, start_time)
            return self._json_error(
                401, 
                "UNAUTHORIZED", 
                "Authorization", 
                "Falta la cabecera de autenticación o la API Key es inválida."
            )

        # Cambiar al contexto del usuario autenticado
        env = request.env.with_user(user)

        # 2. Leer y decodificar el cuerpo JSON de la petición
        try:
            body = json.loads(request.httprequest.data.decode("utf-8"))
        except Exception:
            self._log_api_call(endpoint, user, 422, start_time)
            return self._json_error(
                422, 
                "INVALID_JSON", 
                "body", 
                "El formato del cuerpo de la petición no es un JSON válido."
            )

        partner_rif = body.get("partner_rif")
        external_ref = body.get("external_ref")
        lines = body.get("lines", [])

        # 3. Validar existencia del cliente por RIF
        if not partner_rif:
            self._log_api_call(endpoint, user, 422, start_time)
            return self._json_error(422, "MISSING_FIELD", "partner_rif", "El campo partner_rif es obligatorio.")

        partner = env["res.partner"].search([("vat", "=", partner_rif)], limit=1)
        if not partner:
            self._log_api_call(endpoint, user, 422, start_time)
            return self._json_error(
                422, 
                "PARTNER_NOT_FOUND", 
                "partner_rif", 
                f"No existe un cliente registrado con el RIF '{partner_rif}'."
            )

        # 4. Validar líneas y productos
        if not lines or not isinstance(lines, list):
            self._log_api_call(endpoint, user, 422, start_time)
            return self._json_error(422, "INVALID_LINES", "lines", "Debe incluir al menos una línea de producto válida.")

        order_lines_vals = []
        for idx, line in enumerate(lines):
            default_code = line.get("default_code")
            quantity = line.get("quantity", 0)

            if not default_code:
                self._log_api_call(endpoint, user, 422, start_time)
                return self._json_error(
                    422, 
                    "MISSING_PRODUCT_CODE", 
                    f"lines[{idx}].default_code", 
                    "El código del producto (default_code) es obligatorio en cada línea."
                )

            if not isinstance(quantity, (int, float)) or quantity <= 0:
                self._log_api_call(endpoint, user, 422, start_time)
                return self._json_error(
                    422, 
                    "INVALID_QUANTITY", 
                    f"lines[{idx}].quantity", 
                    "La cantidad debe ser un número mayor a cero."
                )

            # Buscar producto por default_code
            product = env["product.product"].search([("default_code", "=", default_code)], limit=1)
            if not product:
                self._log_api_call(endpoint, user, 422, start_time)
                return self._json_error(
                    422, 
                    "PRODUCT_NOT_FOUND", 
                    f"lines[{idx}].default_code", 
                    f"No existe un producto con el código '{default_code}'[cite: 2]."
                )

            order_lines_vals.append((0, 0, {
                "product_id": product.id,
                "product_uom_qty": quantity,
                "price_unit": product.list_price,
            }))

        # 5. Crear el pedido de venta (Nace como cotización/borrador según nuestro supuesto)[cite: 5]
        try:
            sale_order = env["sale.order"].create({
                "partner_id": partner.id,
                "client_order_ref": external_ref,
                "order_line": order_lines_vals,
            })
            
            # Registrar éxito en el log
            self._log_api_call(endpoint, user, 200, start_time)

            return {
                "success": True,
                "order_id": sale_order.id,
                "order_name": sale_order.name,
                "state": sale_order.state,
            }

        except Exception as e:
            _logger.exception("Error al crear el pedido de venta mediante API")
            self._log_api_call(endpoint, user, 500, start_time)
            return self._json_error(
                500, 
                "INTERNAL_SERVER_ERROR", 
                "server", 
                "Ocurrió un error interno al procesar el pedido."
            )