document.addEventListener('DOMContentLoaded', function() {
    const provinciaSelect = document.getElementById('provincia');
    const municipioSelect = document.getElementById('municipio');
    const repartoSelect = document.getElementById('reparto');
    const metodoEntregaRadios = document.querySelectorAll('input[name="metodo_entrega"]');
    const infoTienda = document.getElementById('info-tienda');
    const infoMensajeria = document.getElementById('info-mensajeria');
    const opcionTienda = document.getElementById('opcion-tienda');
    const opcionMensajeria = document.getElementById('opcion-mensajeria');
    const telefonoInput = document.getElementById('telefono');
    const form = document.getElementById('checkout-form');

    if (telefonoInput) {
        telefonoInput.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '');

            const telefonoWrapper = this.closest('.telefono-input');
            if (telefonoWrapper) {
                if (this.value.length === 8) {
                    telefonoWrapper.classList.remove('error');
                }
            }
        });

        telefonoInput.addEventListener('blur', function() {
            const telefonoWrapper = this.closest('.telefono-input');
            if (telefonoWrapper) {
                if (this.value.length !== 8) {
                    telefonoWrapper.classList.add('error');
                } else {
                    telefonoWrapper.classList.remove('error');
                }
            }
        });
    }

    if (form) {
        form.addEventListener('submit', function(e) {
            if (telefonoInput && telefonoInput.value.length !== 8) {
                e.preventDefault();
                const telefonoWrapper = telefonoInput.closest('.telefono-input');
                if (telefonoWrapper) {
                    telefonoWrapper.classList.add('error');
                }
                telefonoInput.focus();
                return false;
            }
        });
    }

    if (metodoEntregaRadios) {
        metodoEntregaRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const provinciaSelect = document.getElementById('provincia');
                const municipioSelect = document.getElementById('municipio');
                const repartoSelect = document.getElementById('reparto');
                const direccionInput = document.getElementById('direccion');

                if (this.value === 'tienda') {
                    opcionTienda.classList.add('selected');
                    opcionMensajeria.classList.remove('selected');
                    if (infoTienda) infoTienda.style.display = 'block';
                    if (infoMensajeria) infoMensajeria.style.display = 'none';

                    if (provinciaSelect) provinciaSelect.removeAttribute('required');
                    if (municipioSelect) municipioSelect.removeAttribute('required');
                    if (repartoSelect) repartoSelect.removeAttribute('required');
                    if (direccionInput) direccionInput.removeAttribute('required');
                } else if (this.value === 'mensajeria') {
                    opcionMensajeria.classList.add('selected');
                    opcionTienda.classList.remove('selected');
                    if (infoTienda) infoTienda.style.display = 'none';
                    if (infoMensajeria) infoMensajeria.style.display = 'block';

                    if (provinciaSelect) provinciaSelect.setAttribute('required', 'required');
                    if (municipioSelect) municipioSelect.setAttribute('required', 'required');
                    if (repartoSelect) repartoSelect.setAttribute('required', 'required');
                    if (direccionInput) direccionInput.setAttribute('required', 'required');
                }
            });
        });
    }

    if (provinciaSelect) {
        provinciaSelect.addEventListener('change', function() {
            const provinciaId = this.value;
            const selectedOption = this.options[this.selectedIndex];
            const precioBase = selectedOption ? selectedOption.dataset.precio : 0;

            document.getElementById('precio-envio').textContent = formatPrice(parseFloat(precioBase));

            fetch(`${CHECKOUT_URLS.municipios}?provincia_id=${provinciaId}`)
                .then(response => {
                    if (!response.ok) throw new Error('Error al cargar municipios');
                    return response.json();
                })
                .then(data => {
                    municipioSelect.innerHTML = '<option value="">Selecciona un municipio</option>';
                    data.municipios.forEach(mun => {
                        const option = document.createElement('option');
                        option.value = mun.id;
                        option.dataset.precio = mun.precio_adicional;
                        option.textContent = mun.nombre + ' (+' + formatPrice(mun.precio_adicional) + ')';
                        municipioSelect.appendChild(option);
                    });
                    municipioSelect.disabled = false;
                    municipioSelect.required = true;

                    municipioSelect.value = '';
                    repartoSelect.innerHTML = '<option value="">Selecciona un reparto</option>';
                    repartoSelect.disabled = true;
                });
        });
    }

    if (municipioSelect) {
        municipioSelect.addEventListener('change', function() {
            const municipioId = this.value;
            const selectedOption = this.options[this.selectedIndex];
            const precioAdicional = selectedOption ? parseFloat(selectedOption.dataset.precio) : 0;

            const provinciaSelect = document.getElementById('provincia');
            const provinciaOption = provinciaSelect.options[provinciaSelect.selectedIndex];
            const precioBase = provinciaOption ? parseFloat(provinciaOption.dataset.precio) : 0;

            document.getElementById('precio-envio').textContent = formatPrice(precioBase + precioAdicional);

            fetch(`${CHECKOUT_URLS.repartos}?municipio_id=${municipioId}`)
                .then(response => {
                    if (!response.ok) throw new Error('Error al cargar repartos');
                    return response.json();
                })
                .then(data => {
                    repartoSelect.innerHTML = '<option value="">Selecciona un reparto</option>';
                    data.repartos.forEach(rep => {
                        const option = document.createElement('option');
                        option.value = rep.id;
                        option.textContent = rep.nombre;
                        repartoSelect.appendChild(option);
                    });
                    repartoSelect.disabled = false;
                    repartoSelect.required = true;
                });
        });

        const selectedEntrega = document.querySelector('input[name="metodo_entrega"]:checked');
        if (selectedEntrega) {
            const provinciaSelect = document.getElementById('provincia');
            const municipioSelect = document.getElementById('municipio');
            const repartoSelect = document.getElementById('reparto');
            const direccionInput = document.getElementById('direccion');

            if (selectedEntrega.value === 'tienda') {
                opcionTienda.classList.add('selected');
                if (infoTienda) infoTienda.style.display = 'block';
                if (infoMensajeria) infoMensajeria.style.display = 'none';

                if (provinciaSelect) provinciaSelect.removeAttribute('required');
                if (municipioSelect) municipioSelect.removeAttribute('required');
                if (repartoSelect) repartoSelect.removeAttribute('required');
                if (direccionInput) direccionInput.removeAttribute('required');
            } else if (selectedEntrega.value === 'mensajeria') {
                opcionMensajeria.classList.add('selected');
                if (infoTienda) infoTienda.style.display = 'none';
                if (infoMensajeria) infoMensajeria.style.display = 'block';

                if (provinciaSelect) provinciaSelect.setAttribute('required', 'required');
                if (municipioSelect) municipioSelect.setAttribute('required', 'required');
                if (repartoSelect) repartoSelect.setAttribute('required', 'required');
                if (direccionInput) direccionInput.setAttribute('required', 'required');
            }
        }
    }
});
