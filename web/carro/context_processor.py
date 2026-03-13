def importe_total_carro(request):
    total = 0
    if request.user.is_authenticated:
        if "carro" in request.session:
            for key, value in request.session["carro"].items():
                total = total + (float(value["precio"]))
    else:
        # If not authenticated, still show the total if the session has a cart
        if "carro" in request.session:
            for key, value in request.session["carro"].items():
                total = total + (float(value["precio"]))
    return {"importe_total_carro": total}
