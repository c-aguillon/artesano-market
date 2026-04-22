from .carro import Carro


def importe_total_carro(request):
    carro = Carro(request)
    return {
        "importe_total_carro": carro.get_total(),
        "carro_total_items": carro.get_total_items(),
    }
