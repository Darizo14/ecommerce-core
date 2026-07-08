function getCSRFToken() {
    const name = 'csrftoken';
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

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
            const response = await fetch(APP_URLS.cartApi);
            if (!response.ok) throw new Error('Failed to load cart');
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
        totalEl.textContent = formatPrice(data.total);
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
                    <a href="${APP_URLS.productosList}" class="btn btn--primary">Ver productos</a>
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
                        <div class="cart-drawer__item-header">
                            <span class="cart-drawer__item-name">${item.nombre}</span>
                            <span class="cart-drawer__item-price">${formatPrice(item.precio)}</span>
                        </div>
                        ${item.categoria ? `<span class="cart-drawer__item-category">${item.categoria}</span>` : ''}
                        <div class="cart-drawer__item-actions">
                            <div class="qty-selector">
                                <button type="button" class="qty-selector__btn" data-action="decrease" data-item-id="${item.id}" aria-label="Disminuir cantidad">
                                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 6h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                                </button>
                                <span class="qty-selector__value">${item.cantidad}</span>
                                <button type="button" class="qty-selector__btn" data-action="increase" data-item-id="${item.id}" aria-label="Aumentar cantidad">
                                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M6 2v8M2 6h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
                                </button>
                            </div>
                            <a href="${APP_URLS.cartEliminar}${item.id}/" class="cart-drawer__item-remove" aria-label="Eliminar ${item.nombre}">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                    <line x1="10" y1="11" x2="10" y2="17"></line>
                                    <line x1="14" y1="11" x2="14" y2="17"></line>
                                </svg>
                            </a>
                        </div>
                    </div>
                </div>
            `).join('');

            body.querySelectorAll('.qty-selector__btn[data-action]').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    e.preventDefault();
                    const itemId = btn.dataset.itemId;
                    const action = btn.dataset.action;
                    const baseUrl = action === 'increase' ? APP_URLS.cartSumar : APP_URLS.cartRestar;
                    await fetch(`${baseUrl}${itemId}/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': getCSRFToken()
                        }
                    }).then(() => this.loadCart());
                });
            });

            body.querySelectorAll('.cart-drawer__item-remove').forEach(link => {
                link.addEventListener('click', async (e) => {
                    e.preventDefault();
                    const url = link.getAttribute('href');
                    await fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': getCSRFToken()
                        }
                    });
                    this.loadCart();
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
    try {
        const response = await fetch(APP_URLS.cartApi);
        if (!response.ok) throw new Error('Badge fetch failed');
        const data = await response.json();
        updateCartBadge(data.cantidad_total);
    } catch (error) {
        console.warn('Could not load cart badge:', error);
    }
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
            
            const originalHtml = btn.innerHTML;
            btn.innerHTML = 'Agregando...';
            btn.disabled = true;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCSRFToken(),
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'cantidad=1',
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
                btn.innerHTML = originalHtml;
                btn.disabled = false;
            }
        });
    });

    document.querySelectorAll('.dawn-card .btn-add-cart').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();

            const productId = btn.dataset.productId;
            if (!productId) return;
            if (btn.disabled) return;

            const card = btn.closest('.dawn-card');
            const qtyEl = card ? card.querySelector('.qty-selector__value, .quantity-input input') : null;
            const cantidad = qtyEl ? (qtyEl.tagName === 'SPAN' ? parseInt(qtyEl.textContent) : parseInt(qtyEl.value) || 1) : 1;

            const originalHtml = btn.innerHTML;
            btn.innerHTML = 'Agregando...';
            btn.disabled = true;

            try {
                const response = await fetch(`${APP_URLS.cartAgregar}${productId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCSRFToken(),
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `cantidad=${cantidad}`,
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
                btn.innerHTML = originalHtml;
                btn.disabled = false;
            }
        });
    });

    document.getElementById('addToCartForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();

        const form = e.target;
        const btn = form.querySelector('.btn-add-cart');
        const cantidad = form.querySelector('[name="cantidad"]').value;

        const originalHtml = btn.innerHTML;
        btn.innerHTML = 'Agregando...';
        btn.disabled = true;

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `cantidad=${cantidad}`,
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
            btn.innerHTML = originalHtml;
            btn.disabled = false;
        }
    });
});

function increaseQty(productId) {
    const span = document.getElementById('cantidad-' + productId);
    if (!span) return;
    const max = parseInt(span.dataset.stock);
    const current = parseInt(span.textContent);
    if (current < max) {
        const next = current + 1;
        span.textContent = next;
        const hidden = document.getElementById('hidden-cantidad-' + productId);
        if (hidden) hidden.value = next;
    }
}

function decreaseQty(productId) {
    const span = document.getElementById('cantidad-' + productId);
    if (!span) return;
    const current = parseInt(span.textContent);
    if (current > 1) {
        const next = current - 1;
        span.textContent = next;
        const hidden = document.getElementById('hidden-cantidad-' + productId);
        if (hidden) hidden.value = next;
    }
}