from dateutil.parser import parse

from odoo import fields, http
from odoo.http import request


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