from django.contrib import admin

from .models import Contacto


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "correo", "asunto", "fecha_envio", "revisado")
    list_filter = ("revisado",)
    search_fields = ("nombre", "correo", "asunto")
    # La fecha se genera sola (auto_now_add), no tiene sentido dejarla editable.
    readonly_fields = ("fecha_envio",)

    # Acción en lote: permite seleccionar varios mensajes en el listado
    # y marcarlos como revisados con un solo clic, en vez de entrar
    # a cada uno por separado.
    actions = ["marcar_como_revisado"]

    @admin.action(description="Marcar seleccionados como revisados")
    def marcar_como_revisado(self, request, queryset):
        queryset.update(revisado=True)
