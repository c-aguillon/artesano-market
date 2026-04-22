from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class Carro:
    SESSION_KEY = "carro"

    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.carro = self.session.get(self.SESSION_KEY, {})
        if not isinstance(self.carro, dict):
            self.carro = {}
        self._normalizar_carro()

    def agregar(self, producto):
        producto_id = str(producto.id)
        item = self.carro.get(producto_id)

        if item is None:
            self.carro[producto_id] = self._crear_item(producto, cantidad=1)
        else:
            cantidad_actual = int(item.get("cantidad", 0))
            nueva_cantidad = min(cantidad_actual + 1, producto.stock)
            self.carro[producto_id] = self._crear_item(producto, cantidad=nueva_cantidad)

        self.guardar_carro()

    def eliminar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carro:
            del self.carro[producto_id]
            self.guardar_carro()

    def restar_producto(self, producto):
        producto_id = str(producto.id)
        item = self.carro.get(producto_id)

        if item is None:
            return

        cantidad_actual = int(item.get("cantidad", 0))
        nueva_cantidad = cantidad_actual - 1

        if nueva_cantidad < 1:
            self.eliminar(producto)
            return

        self.carro[producto_id] = self._crear_item(producto, cantidad=nueva_cantidad)
        self.guardar_carro()

    def limpiar_carro(self):
        self.carro = {}
        self.session[self.SESSION_KEY] = self.carro
        self.session.modified = True

    def set_items(self, productos_por_id, items):
        nuevo_carro = {}

        for item in items:
            producto_id = str(item.get("producto_id", ""))
            producto = productos_por_id.get(producto_id)
            if producto is None or producto.stock <= 0:
                continue

            cantidad = max(1, min(int(item.get("cantidad", 1)), producto.stock))
            nuevo_carro[producto_id] = self._crear_item(producto, cantidad)

        self.carro = nuevo_carro
        self.guardar_carro()

    def get_items(self):
        items = []
        for item in self.carro.values():
            cantidad = int(item.get("cantidad", 0))
            precio_unitario = self._to_decimal(item.get("precio_unitario", "0"))
            subtotal = self._calcular_subtotal(precio_unitario, cantidad)
            items.append({
                "producto_id": item["producto_id"],
                "nombre": item["nombre"],
                "precio_unitario": self._format_decimal(precio_unitario),
                "precio": self._format_decimal(subtotal),
                "subtotal": self._format_decimal(subtotal),
                "cantidad": cantidad,
                "imagen": item.get("imagen", ""),
            })
        return items

    def get_total(self):
        total = sum(
            (self._to_decimal(item["subtotal"]) for item in self.get_items()),
            Decimal("0.00"),
        )
        return self._format_decimal(total)

    def get_total_items(self):
        return sum(item["cantidad"] for item in self.get_items())

    def guardar_carro(self):
        self.session[self.SESSION_KEY] = self.carro
        self.session.modified = True

    def _normalizar_carro(self):
        carro_normalizado = {}

        for key, value in self.carro.items():
            producto_id = str(value.get("producto_id", key))
            nombre = value.get("nombre", "")
            cantidad = max(int(value.get("cantidad", 1)), 0)
            imagen = value.get("imagen", "")

            precio_unitario = value.get("precio_unitario")
            if precio_unitario is None:
                subtotal_original = self._to_decimal(value.get("precio", "0"))
                if cantidad > 0:
                    precio_unitario = self._format_decimal(subtotal_original / cantidad)
                else:
                    precio_unitario = "0.00"

            precio_unitario_decimal = self._to_decimal(precio_unitario)
            subtotal = self._calcular_subtotal(precio_unitario_decimal, cantidad)

            carro_normalizado[producto_id] = {
                "producto_id": int(producto_id),
                "nombre": nombre,
                "precio_unitario": self._format_decimal(precio_unitario_decimal),
                "precio": self._format_decimal(subtotal),
                "cantidad": cantidad,
                "imagen": imagen,
            }

        self.carro = carro_normalizado
        self.guardar_carro()

    def _crear_item(self, producto, cantidad):
        precio_unitario = self._to_decimal(producto.precio)
        subtotal = self._calcular_subtotal(precio_unitario, cantidad)

        return {
            "producto_id": producto.id,
            "nombre": producto.nombre,
            "precio_unitario": self._format_decimal(precio_unitario),
            "precio": self._format_decimal(subtotal),
            "cantidad": cantidad,
            "imagen": producto.imagen.url if producto.imagen else "",
        }

    @staticmethod
    def _calcular_subtotal(precio_unitario, cantidad):
        return (precio_unitario * Decimal(cantidad)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _to_decimal(value):
        try:
            return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0.00")

    @staticmethod
    def _format_decimal(value):
        return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")
