from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class Carro:
    @staticmethod
    def a_decimal(value, default="0.00"):
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal(default)

    @staticmethod
    def formatear(value):
        return str(Carro.a_decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def crear_item(producto, cantidad=1):
        cantidad = max(int(cantidad or 1), 1)
        precio_unitario = Carro.a_decimal(producto.precio)
        subtotal = precio_unitario * cantidad
        return {
            "producto_id": producto.id,
            "nombre": producto.nombre,
            "precio_unitario": Carro.formatear(precio_unitario),
            "precio": Carro.formatear(subtotal),
            "subtotal": Carro.formatear(subtotal),
            "cantidad": cantidad,
            "imagen": producto.imagen.url if producto.imagen else "",
        }

    def __init__(self, request):
        self.request = request
        self.session = request.session
        carro = self.session.get("carro") or {}
        self.carro = self._normalizar_carro(carro)
        self.guardar_carro()

    def _normalizar_item(self, producto_id, value):
        value = value or {}
        cantidad = max(int(value.get("cantidad", 1) or 1), 1)
        precio_unitario = value.get("precio_unitario")
        precio_total = value.get("subtotal", value.get("precio", "0.00"))

        if precio_unitario is None:
            total = self.a_decimal(precio_total)
            precio_unitario = total / cantidad if cantidad else total

        subtotal = self.a_decimal(precio_unitario) * cantidad
        return {
            "producto_id": int(value.get("producto_id", producto_id)),
            "nombre": value.get("nombre", ""),
            "precio_unitario": self.formatear(precio_unitario),
            "precio": self.formatear(subtotal),
            "subtotal": self.formatear(subtotal),
            "cantidad": cantidad,
            "imagen": value.get("imagen", ""),
        }

    def _normalizar_carro(self, carro):
        normalizado = {}
        for key, value in (carro or {}).items():
            producto_id = str(value.get("producto_id", key))
            normalizado[producto_id] = self._normalizar_item(producto_id, value)
        return normalizado

    def agregar(self, producto):
        producto_id = str(producto.id)
        if producto_id not in self.carro:
            self.carro[producto_id] = self.crear_item(producto, cantidad=1)
        else:
            item = self._normalizar_item(producto_id, self.carro[producto_id])
            item["cantidad"] += 1
            subtotal = self.a_decimal(item["precio_unitario"]) * item["cantidad"]
            item["precio"] = self.formatear(subtotal)
            item["subtotal"] = self.formatear(subtotal)
            item["nombre"] = producto.nombre
            item["imagen"] = producto.imagen.url if producto.imagen else ""
            self.carro[producto_id] = item
        self.guardar_carro()

    def guardar_carro(self):
        self.session["carro"] = self.carro
        self.session.modified = True

    def reemplazar(self, carro_dict):
        self.carro = self._normalizar_carro(carro_dict)
        self.guardar_carro()

    def eliminar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carro:
            del self.carro[producto_id]
            self.guardar_carro()

    def restar_producto(self, producto):
        producto_id = str(producto.id)
        if producto_id not in self.carro:
            return

        item = self._normalizar_item(producto_id, self.carro[producto_id])
        item["cantidad"] -= 1
        if item["cantidad"] < 1:
            self.eliminar(producto)
            return

        subtotal = self.a_decimal(item["precio_unitario"]) * item["cantidad"]
        item["precio"] = self.formatear(subtotal)
        item["subtotal"] = self.formatear(subtotal)
        self.carro[producto_id] = item
        self.guardar_carro()

    def limpiar_carro(self):
        self.carro = {}
        self.guardar_carro()
