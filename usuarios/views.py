from django.shortcuts import render


def login_view(request):
    # TODO: procesar el formulario y autenticar con django.contrib.auth
    return render(request, "usuarios/login.html")


def registro_view(request):
    # TODO: procesar el formulario y crear el Usuario real
    return render(request, "usuarios/registro.html")
