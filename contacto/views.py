from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactoForm


def index(request):
    if request.method == "POST":
        form = ContactoForm(request.POST)
        if form.is_valid():
            # form.save() crea el registro de Contacto en la base de
            # datos con los datos ya validados del formulario.
            form.save()
            messages.success(request, "Tu mensaje fue enviado. Te responderemos pronto.")
            # Se redirige (patron Post/Redirect/Get) para que si la
            # persona recarga la pagina despues de enviar, no se
            # vuelva a enviar el mismo formulario por accidente.
            return redirect("contacto:index")
    else:
        form = ContactoForm()

    return render(request, "contacto/formulario.html", {"form": form})
