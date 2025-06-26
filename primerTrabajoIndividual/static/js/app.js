/**
 * funcion para agregar especilidad de instructores
 * como "etiquetas"  
 */
const especialidades = [];

    function agregarEspecialidad() {
        const input = document.getElementById("inputEspecialidad");
        const valor = input.value.trim();

        // Validación
        if (valor === "") {
            alert("Ingresa una especialidad.");
            return;
        }
        if (especialidades.includes(valor)) {
            alert("Esa especialidad ya fue agregada.");
            input.value = "";
            return;
        }

        especialidades.push(valor);
        actualizarVistaEspecialidades();
        input.value = "";
    }

    function eliminarEspecialidad(valor) {
        const index = especialidades.indexOf(valor);
        if (index !== -1) {
            especialidades.splice(index, 1);
            actualizarVistaEspecialidades();
        }
    }

    function actualizarVistaEspecialidades() {
        const contenedor = document.getElementById("listaEspecialidades");
        contenedor.innerHTML = "";  // Limpiar todo

        especialidades.forEach(especialidad => {
            const div = document.createElement("div");
            div.className = "especialidad";

            const texto = document.createElement("span");
            texto.textContent = especialidad;

            const botonEliminar = document.createElement("span");
            botonEliminar.className = "eliminar";
            botonEliminar.textContent = "✖";
            botonEliminar.onclick = () => eliminarEspecialidad(especialidad);

            div.appendChild(texto);
            div.appendChild(botonEliminar);
            contenedor.appendChild(div);
        });

        // Actualizar campo oculto
        document.getElementById("especialidadesHidden").value = JSON.stringify(especialidades);
    }