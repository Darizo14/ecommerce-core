document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('productosSidebar');
    const overlay = document.getElementById('productosSidebarOverlay');
    const toggleBtn = document.getElementById('mobileFilterToggle');
    const closeBtn = document.getElementById('mobileFilterClose');

    if (toggleBtn && sidebar && overlay) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.add('productos-sidebar--open');
            overlay.classList.add('productos-sidebar-overlay--visible');
            document.body.style.overflow = 'hidden';
        });
    }

    function closeFilters() {
        if (sidebar) sidebar.classList.remove('productos-sidebar--open');
        if (overlay) overlay.classList.remove('productos-sidebar-overlay--visible');
        document.body.style.overflow = '';
    }

    if (closeBtn) closeBtn.addEventListener('click', closeFilters);
    if (overlay) overlay.addEventListener('click', closeFilters);
});

function limpiarFiltros() {
    document.getElementById('form-filtro').reset();
    window.location.href = "/productos/";
}
