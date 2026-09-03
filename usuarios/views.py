from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm, RegistroForm
from .models import Usuario


def login_view(request):
    # Si la persona ya inicio sesion, no tiene sentido mostrarle el
    # formulario de login de nuevo: se le redirige directo al Home.
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # authenticate() revisa usuario y contraseña contra la base
            # de datos y devuelve el objeto Usuario si son correctos,
            # o None si no lo son. Aca se usa el correo como "username"
            # porque en el registro se guarda el correo en ese campo.
            usuario = authenticate(request, username=email, password=password)

            if usuario is not None:
                # login() crea la sesion del usuario (la cookie que
                # mantiene la sesion iniciada mientras navega el sitio).
                login(request, usuario)
                messages.success(request, f"Bienvenido, {usuario.first_name or usuario.username}.")
                return redirect("core:home")
            else:
                form.add_error(None, "Correo o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(request, "usuarios/login.html", {"form": form})


def registro_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data

            # Se crea el usuario nuevo. El correo se usa tambien como
            # username porque AbstractUser exige un username unico y
            # este formulario no le pide uno aparte a la persona.
            usuario = Usuario(
                username=datos["email"],
                email=datos["email"],
                first_name=datos["nombre"],
            )
            # set_password() hashea la contraseña antes de guardarla.
            # Nunca se asigna la contraseña directo (usuario.password = "...")
            # porque eso la guardaria en texto plano.
            usuario.set_password(datos["password1"])
            usuario.save()

            # Se inicia sesion automaticamente despues de registrarse,
            # para no obligar a la persona a loguearse de nuevo.
            login(request, usuario)
            messages.success(request, "Cuenta creada correctamente. ¡Bienvenido!")
            return redirect("core:home")
    else:
        form = RegistroForm()

    return render(request, "usuarios/registro.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada.")
    return redirect("core:home")
