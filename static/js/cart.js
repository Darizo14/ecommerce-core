const cartDrawer = {
    drawer: null,
    overlay: null,
    isOpen: false,

    init() {
        this.drawer = document.getElementById('cartDrawer');
        this.overlay = document.getElementById('cartOverlay');
        this.bindEvents();
    },

    bindEvents() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    },

    open() {
        this.loadCart();
        this.drawer.classList.add('active');
        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        this.isOpen = true;
    },

    close() {
        this.drawer.classList.remove('active');
        this.overlay.classList.remove('active');
        document.body.style.overflow = '';
        this.isOpen = false;
    },

    async loadCart() {
        try {
            const response = await fetch('/carrito/api/obtener/');
            const data = await response.json();
            this.renderCart(data);
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    },

    renderCart(data) {
        const body = this.drawer.querySelector('.cart-drawer__body');
        const countEl = this.drawer.querySelector('.cart-drawer__count');
        const totalEl = this.drawer.querySelector('.cart-drawer__total-value');
        const footer = this.drawer.querySelector('.cart-drawer__footer');

        countEl.textContent = data.cantidad_total;
        totalEl.textContent = `$${data.total.toFixed(2)}`;
        updateCartBadge(data.cantidad_total);

        if (data.productos.length === 0) {
            body.innerHTML = `
                <div class="cart-drawer__empty">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="9" cy="21" r="1"></circle>
                        <circle cx="20" cy="21" r="1"></circle>
                        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                    </svg>
                    <p>Tu carrito está vacío</p>
                    <a href="/productos/" class="btn btn--primary">Ver productos</a>
                </div>
            `;
            footer.style.display = 'none';
        } else {
            footer.style.display = 'block';
            body.innerHTML = data.productos.map(item => `
                <div class="cart-drawer__item" data-id="${item.id}">
                    <div class="cart-drawer__item-image">
                        ${item.imagen ? `<img src="${item.imagen}" alt="${item.nombre}">` : '<div class="imagen-placeholder"></div>'}
                    </div>
                    <div class="cart-drawer__item-info">
                        <span class="cart-drawer__item-name">${item.nombre}</span>
                        <span class="cart-drawer__item-price">$${item.precio}</span>
                        <div class="cart-drawer__item-qty">
                            <a href="/carrito/restar/${item.id}/" class="cart-drawer__qty-btn" data-action="decrease">−</a>
                            <span class="cart-drawer__qty-value">${item.cantidad}</span>
                            <a href="/carrito/sumar/${item.id}/" class="cart-drawer__qty-btn" data-action="increase">+</a>
                        </div>
                    </div>
                    <a href="/carrito/eliminar/${item.id}/" class="cart-drawer__item-remove">Eliminar</a>
                </div>
            `).join('');

            body.querySelectorAll('a[data-action]').forEach(link => {
                link.addEventListener('click', async (e) => {
                    e.preventDefault();
                    const url = link.getAttribute('href');
                    await fetch(url, { 
                        headers: { 'X-Requested-With': 'XMLHttpRequest' }
                    }).then(() => this.loadCart());
                });
            });

            body.querySelectorAll('.cart-drawer__item-remove').forEach(link => {
                link.addEventListener('click', async (e) => {
                    e.preventDefault();
                    const url = link.getAttribute('href');
                    await fetch(url, {
                        headers: { 'X-Requested-With': 'XMLHttpRequest' }
                    }).then(() => this.loadCart());
                });
            });
        }
    }
};

const toast = {
    show(message, type = 'success', duration = 4000) {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const icons = {
            success: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
            error: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
            warning: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
        };

        const toastEl = document.createElement('div');
        toastEl.className = `toast toast--${type}`;
        toastEl.innerHTML = `
            <span class="toast__icon">${icons[type]}</span>
            <div class="toast__content">
                <span class="toast__title">${type === 'success' ? '¡Éxito!' : type === 'error' ? 'Error' : 'Atención'}</span>
                <span class="toast__message">${message}</span>
            </div>
            <button class="toast__close">&times;</button>
        `;

        container.appendChild(toastEl);

        toastEl.querySelector('.toast__close').addEventListener('click', () => {
            this.hide(toastEl);
        });

        if (duration > 0) {
            setTimeout(() => this.hide(toastEl), duration);
        }

        return toastEl;
    },

    hide(toastEl) {
        toastEl.classList.add('hiding');
        setTimeout(() => toastEl.remove(), 300);
    }
};

function updateCartBadge(cantidad) {
    const badge = document.getElementById('cartCount');
    if (cantidad > 0) {
        badge.textContent = cantidad;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

async function initCartBadge() {
    const response = await fetch('/carrito/api/obtener/');
    const data = await response.json();
    updateCartBadge(data.cantidad_total);
}

document.addEventListener('DOMContentLoaded', () => {
    cartDrawer.init();
    initCartBadge();

    document.getElementById('cartToggle').addEventListener('click', (e) => {
        e.preventDefault();
        cartDrawer.open();
    });

    document.getElementById('cartClose').addEventListener('click', () => {
        cartDrawer.close();
    });

    document.getElementById('cartOverlay').addEventListener('click', () => {
        cartDrawer.close();
    });

    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            let url = btn.getAttribute('href');
            if (!url) return;

            e.preventDefault();
            
            const originalText = btn.textContent;
            btn.textContent = 'Agregando...';
            btn.disabled = true;

            try {
                const response = await fetch(url, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const data = await response.json();

                if (data.success) {
                    updateCartBadge(data.cantidad_total);
                    toast.show(data.message, 'success');
                } else {
                    toast.show(data.error || 'Error al agregar', 'error');
                }
            } catch (error) {
                toast.show('Error de conexión', 'error');
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    });

    document.getElementById('addToCartForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const form = e.target;
        const btn = form.querySelector('.add-to-cart');
        const cantidad = form.querySelector('[name="cantidad"]').value;
        let url = form.action;
        url = `${url}?cantidad=${cantidad}`;
        
        const originalText = btn.textContent;
        btn.textContent = 'Agregando...';
        btn.disabled = true;

        try {
            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await response.json();

            if (data.success) {
                updateCartBadge(data.cantidad_total);
                toast.show(data.message, 'success');
            } else {
                toast.show(data.error || 'Error al agregar', 'error');
            }
        } catch (error) {
            toast.show('Error de conexión', 'error');
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    });

    // Cuando agregues un producto (desde lista de productos)
    async function addToCart(productId) {
        const response = await fetch(`/carrito/agregar/${productId}/`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await response.json();
        
        if (data.success) {
            updateCartBadge(data.cantidad_total);
            toast.show(data.message);
        }
    }
});