function log(text, outputId) {
    const output = document.getElementById(outputId);
    output.textContent = text;
}

function insertarEjemplo() {
    const ejemploJSON = `{
        "nombre": "Juan", 
        "apellido": "Perez",
        "edad": 30,
        "activo": true
    }`;
    document.getElementById("inputJson").value = ejemploJSON;
    log("✅ Ejemplo insertado, ahora puedes guardar.", "outputClient");
}

function guardarUsuario() {
    const input = document.getElementById("inputJson").value.trim();
    if (!input) {
        log("❌ El campo está vacío, ingresa un JSON válido.", "outputClient");
        return;
    }
    try {
        const nuevo = JSON.parse(input);
        const guardado = JSON.parse(localStorage.getItem("usuarios")) || [];
        guardado.push(nuevo);
        localStorage.setItem("usuarios", JSON.stringify(guardado));
        log("✅ Dato guardado correctamente.", "outputClient");
        mostrarUsuarios();
    } catch (error) {
        log("❌ JSON inválido: " + error.message, "outputClient");
    }
}

function mostrarUsuarios() {
    const lista = document.getElementById("listaUsuarios");
    lista.innerHTML = "";
    const datos = JSON.parse(localStorage.getItem("usuarios")) || [];

    datos.forEach((item, index) => {
        const li = document.createElement("li");
        li.textContent = JSON.stringify(item);

        const btnEditar = document.createElement("button");
        btnEditar.textContent = "Editar";
        btnEditar.onclick = () => editarUsuario(index);

        const btnEliminar = document.createElement("button");
        btnEliminar.textContent = "Eliminar";
        btnEliminar.onclick = () => eliminarUsuario(index);

        li.appendChild(btnEditar);
        li.appendChild(btnEliminar);
        lista.appendChild(li);
    });
}

function editarUsuario(index) {
    const nuevoValor = prompt("Nuevo objeto JSON:");
    try {
        const obj = JSON.parse(nuevoValor);
        const datos = JSON.parse(localStorage.getItem("usuarios")) || [];
        datos[index] = obj;
        localStorage.setItem("usuarios", JSON.stringify(datos));
        log("📝 Usuario actualizado.", "outputClient");
        mostrarUsuarios();
    } catch (e) {
        log("❌ JSON inválido: " + e.message, "outputClient");
    }
}

function eliminarUsuario(index) {
    const datos = JSON.parse(localStorage.getItem("usuarios")) || [];
    datos.splice(index, 1);
    localStorage.setItem("usuarios", JSON.stringify(datos));
    log("🗑 Usuario eliminado.", "outputClient");
    mostrarUsuarios();
}

async function obtenerDatos() {
    const url = "https://rickandmortyapi.com/api/character";
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("HTTP error: " + response.status);

        const dataString = await response.text();
        log("[Data String] Recibido del servidor:\n" + dataString, "outputServer");

        let objetoJs;
        try {
            objetoJs = JSON.parse(dataString);
        } catch (e) {
            throw new Error("El JSON recibido es inválido");
        }

        log("[objeto js] parseando con JSON.parse():\n" + JSON.stringify(objetoJs, null, 2), "outputServer");

        const nuevaDataString = JSON.stringify(objetoJs);
        localStorage.setItem("usuario", nuevaDataString);
        log("✅ [Simulado] Datos guardados como JSON.", "outputServer");

    } catch (error) {
        log("❌ Error al procesar los datos: " + error.message, "outputServer");
    }
}

function cargarDatos() {
    const jsonGuardado = localStorage.getItem("usuario");
    if (!jsonGuardado) {
        log("🔺 No hay datos guardados en localStorage.", "outputClient");
        return;
    }

    log("🔹 {Data String} desde localStorage:\n" + jsonGuardado, "outputClient");
    try {
        const objetoJs = JSON.parse(jsonGuardado);
        const jsonString = JSON.stringify(objetoJs, null, 2);
        log("🔸 [objetoJs] parseado:\n" + jsonString, "outputClient");
        log("✅ Datos listos para enviar al servidor.", "outputClient");
    } catch (error) {
        log("❌ Error al procesar entrada: " + error.message, "outputClient");
    }
}

window.onload = mostrarUsuarios;
