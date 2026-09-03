/*
 * Carrito de compras de Vinyl Hub.
 *
 * El carrito se guarda completo en localStorage del navegador, no en la
 * base de datos. Esto significa que el carrito es propio de cada
 * navegador/computador: si el mismo cliente entra desde otro dispositivo,
 * no va a ver el mismo carrito. Asi lo pidieron las instrucciones del
 * proyecto (usar localStorage, sin backend para el carrito).
 *
 * Estructura que se guarda en localStorage, como texto JSON:
 * [
 *   { id: "1", nombre: "Walk Among Us", precio: "89.90", cantidad: 2 },
 *   { id: "2", nombre: "Californication", precio: "95.50", cantidad: 1 }
 * ]
 */

const CLAVE_CARRITO = "vinylhub_carrito";

// Lee el carrito actual desde localStorage. Si no hay nada guardado
// todavia (primera visita), devuelve una lista vacia en vez de fallar.
function obtenerCarrito() {
    const datos = localStorage.getItem(CLAVE_CARRITO);
    if (!datos) {
        return [];
    }
    try {
        return JSON.parse(datos);
    } catch (error) {
        // Si el contenido guardado esta corrupto por algun motivo,
        // se reinicia el carrito en vez de romper la pagina.
        return [];
    }
}

// Guarda la lista completa del carrito en localStorage, convertida a texto.
function guardarCarrito(carrito) {
    localStorage.setItem(CLAVE_CARRITO, JSON.stringify(carrito));
}

// Agrega un producto al carrito. Si el producto ya estaba, solo le suma
// una unidad a la cantidad en vez de crear una fila duplicada.
function agregarAlCarrito(id, nombre, precio) {
    const carrito = obtenerCarrito();
    const existente = carrito.find((item) => item.id === id);

    if (existente) {
        existente.cantidad += 1;
    } else {
        carrito.push({ id: id, nombre: nombre, precio: precio, cantidad: 1 });
    }

    guardarCarrito(carrito);
    actualizarContadorCarrito();
    renderizarCarrito();
}

// Saca un producto del carrito por completo (todas sus unidades).
function eliminarDelCarrito(id) {
    let carrito = obtenerCarrito();
    carrito = carrito.filter((item) => item.id !== id);
    guardarCarrito(carrito);
    actualizarContadorCarrito();
    renderizarCarrito();
}

// Cambia la cantidad de un producto ya agregado. Si la cantidad nueva es
// 0 o menos, se elimina el producto del carrito directamente.
function cambiarCantidad(id, nuevaCantidad) {
    const carrito = obtenerCarrito();
    const item = carrito.find((item) => item.id === id);

    if (!item) {
        return;
    }

    if (nuevaCantidad <= 0) {
        eliminarDelCarrito(id);
        return;
    }

    item.cantidad = nuevaCantidad;
    guardarCarrito(carrito);
    actualizarContadorCarrito();
    renderizarCarrito();
}

// Suma la cantidad de todos los productos y actualiza el numerito
// (badge) que se ve al lado de "Carrito" en el navbar, en todas las
// paginas del sitio (el navbar esta en base.html, se comparte siempre).
function actualizarContadorCarrito() {
    const carrito = obtenerCarrito();
    const totalUnidades = carrito.reduce((suma, item) => suma + item.cantidad, 0);

    const contador = document.getElementById("contador-carrito");
    if (contador) {
        contador.textContent = totalUnidades;
    }
}

// Dibuja el contenido del carrito dentro de la pagina /carrito/.
// En cualquier otra pagina del sitio, el contenedor "carrito-contenedor"
// no existe, asi que esta funcion no hace nada (por eso el "if" al inicio).
function renderizarCarrito() {
    const contenedor = document.getElementById("carrito-contenedor");
    if (!contenedor) {
        return;
    }

    const carrito = obtenerCarrito();

    if (carrito.length === 0) {
        contenedor.innerHTML = "<p>Tu carrito está vacío.</p>";
        document.getElementById("carrito-total").textContent = "$0";
        return;
    }

    let html = "";
    let total = 0;

    carrito.forEach((item) => {
        const subtotal = item.cantidad * parseFloat(item.precio);
        total += subtotal;

        html += `
            <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                <div>
                    <strong>${item.nombre}</strong><br>
                    <span class="text-secondary">$${item.precio} c/u</span>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <input type="number" min="1" value="${item.cantidad}"
                           class="form-control form-control-sm"
                           style="width: 70px;"
                           onchange="cambiarCantidad('${item.id}', parseInt(this.value))">
                    <span>$${subtotal.toFixed(2)}</span>
                    <button class="btn btn-sm btn-outline-danger" onclick="eliminarDelCarrito('${item.id}')">
                        Quitar
                    </button>
                </div>
            </div>
        `;
    });

    contenedor.innerHTML = html;
    document.getElementById("carrito-total").textContent = "$" + total.toFixed(2);
}

// Busca todos los botones "Añadir al carrito" que haya en la pagina
// actual (puede haber varios: uno por cada card de producto en el
// listado, o uno solo en el detalle) y les conecta el evento de click.
// Los datos del producto se leen de los atributos data-* del boton,
// que las plantillas Django ya rellenan con los valores reales.
function conectarBotonesAgregar() {
    const botones = document.querySelectorAll(".btn-add-cart, .btn-agregar-carrito");

    botones.forEach((boton) => {
        boton.addEventListener("click", () => {
            const id = boton.dataset.productoId;
            const nombre = boton.dataset.productoNombre;
            const precio = boton.dataset.productoPrecio;
            agregarAlCarrito(id, nombre, precio);
        });
    });
}

// Este bloque se ejecuta apenas el HTML de la pagina termina de cargar,
// en cualquier pagina del sitio (esta cargado desde base.html).
document.addEventListener("DOMContentLoaded", () => {
    actualizarContadorCarrito();
    renderizarCarrito();
    conectarBotonesAgregar();
});
