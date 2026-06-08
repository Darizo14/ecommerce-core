(function() {
    'use strict';

    var form = document.getElementById('form-filtro');
    var contentDiv = document.getElementById('productos-main-content');
    var mainEl = document.getElementById('productosMain');
    var clearBtn = document.getElementById('clearFilters');
    var ordenInput = document.getElementById('ordenInput');

    if (!form || !contentDiv) return;

    form.addEventListener('submit', function(e) { e.preventDefault(); });

    /* ---- Mobile sidebar toggle ---- */
    var sidebar = document.getElementById('productosSidebar');
    var overlay = document.getElementById('productosSidebarOverlay');
    var toggleBtn = document.getElementById('mobileFilterToggle');
    var closeBtn = document.getElementById('mobileFilterClose');

    function openFilters() {
        if (sidebar) sidebar.classList.add('productos-sidebar--open');
        if (overlay) overlay.classList.add('productos-sidebar-overlay--visible');
        document.body.style.overflow = 'hidden';
    }

    function closeFilters() {
        if (sidebar) sidebar.classList.remove('productos-sidebar--open');
        if (overlay) overlay.classList.remove('productos-sidebar-overlay--visible');
        document.body.style.overflow = '';
    }

    if (toggleBtn && sidebar && overlay) {
        toggleBtn.addEventListener('click', openFilters);
    }
    if (closeBtn) closeBtn.addEventListener('click', closeFilters);
    if (overlay) overlay.addEventListener('click', closeFilters);

    /* ---- Debounce utility ---- */
    function debounce(fn, ms) {
        var timer;
        return function() {
            var ctx = this, args = arguments;
            clearTimeout(timer);
            timer = setTimeout(function() { fn.apply(ctx, args); }, ms);
        };
    }

    /* ---- Build URL from form ---- */
    function buildFilterUrl() {
        var params = new URLSearchParams(new FormData(form));
        var qs = params.toString();
        return qs ? '?' + qs : '/productos/';
    }

    /* ---- Fetch filtered products via AJAX ---- */
    var currentRequest = null;

    function applyFilters() {
        if (currentRequest) {
            currentRequest.abort();
        }

        var url = buildFilterUrl();

        window.history.replaceState({}, '', url);

        if (mainEl) mainEl.classList.add('productos-main--loading');

        currentRequest = new XMLHttpRequest();
        currentRequest.open('GET', url, true);
        currentRequest.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        currentRequest.onload = function() {
            if (currentRequest.status >= 200 && currentRequest.status < 400) {
                contentDiv.innerHTML = currentRequest.responseText;
                attachPaginationHandlers();
            }
            if (mainEl) mainEl.classList.remove('productos-main--loading');
            currentRequest = null;
        };
        currentRequest.onerror = function() {
            if (mainEl) mainEl.classList.remove('productos-main--loading');
            currentRequest = null;
        };
        currentRequest.send();
    }

    var debouncedFilter = debounce(applyFilters, 300);

    function onFilterChange() {
        updateClearBtn();
        debouncedFilter();
    }

    /* ---- Attach events to form inputs ---- */
    var checkboxes = form.querySelectorAll('input[type="checkbox"]');
    for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].addEventListener('change', function() {
            onFilterChange();
        });
    }

    var priceInputs = form.querySelectorAll('input[type="number"]');
    for (var j = 0; j < priceInputs.length; j++) {
        priceInputs[j].addEventListener('input', onFilterChange);
    }

    /* ---- Custom sort dropdown ---- */
    var dropdown = document.getElementById('sortDropdown');
    var trigger = document.getElementById('sortDropdownTrigger');
    var menu = document.getElementById('sortDropdownMenu');
    var label = document.getElementById('sortDropdownLabel');
    var options;

    function getOptions() {
        if (!options && menu) {
            options = menu.querySelectorAll('li');
        }
        return options || [];
    }

    function getSortValue() {
        return ordenInput ? ordenInput.value : '';
    }

    function updateDropdownLabel() {
        var val = getSortValue();
        var opts = getOptions();
        for (var i = 0; i < opts.length; i++) {
            if (opts[i].getAttribute('data-value') === val) {
                label.textContent = opts[i].textContent;
                opts[i].setAttribute('aria-selected', 'true');
            } else {
                opts[i].setAttribute('aria-selected', 'false');
            }
        }
    }

    function setSortValue(val) {
        if (ordenInput) {
            ordenInput.value = val;
        }
        updateDropdownLabel();
    }

    function openDropdown() {
        if (!dropdown || !trigger || !menu) return;
        dropdown.classList.add('sort-dropdown--open');
        trigger.setAttribute('aria-expanded', 'true');
    }

    function closeDropdown() {
        if (!dropdown || !trigger || !menu) return;
        dropdown.classList.remove('sort-dropdown--open');
        trigger.setAttribute('aria-expanded', 'false');
    }

    function toggleDropdown() {
        if (dropdown.classList.contains('sort-dropdown--open')) {
            closeDropdown();
        } else {
            openDropdown();
        }
    }

    if (trigger && menu && dropdown) {
        trigger.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleDropdown();
        });

        var opts = getOptions();
        for (var k = 0; k < opts.length; k++) {
            opts[k].addEventListener('click', function() {
                var val = this.getAttribute('data-value');
                setSortValue(val);
                closeDropdown();
                updateClearBtn();
                applyFilters();
            });
        }

        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                closeDropdown();
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeDropdown();
            }
        });

        trigger.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleDropdown();
            }
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                if (!dropdown.classList.contains('sort-dropdown--open')) {
                    openDropdown();
                }
                var opts = getOptions();
                var currentIdx = -1;
                for (var i = 0; i < opts.length; i++) {
                    if (opts[i].getAttribute('aria-selected') === 'true') {
                        currentIdx = i;
                        break;
                    }
                }
                var nextIdx = e.key === 'ArrowDown'
                    ? Math.min(currentIdx + 1, opts.length - 1)
                    : Math.max(currentIdx - 1, 0);
                var nextVal = opts[nextIdx].getAttribute('data-value');
                setSortValue(nextVal);
                updateClearBtn();
                applyFilters();
            }
        });

        updateDropdownLabel();
    }

    /* ---- Enable/disable clear button ---- */
    function updateClearBtn() {
        if (!clearBtn) return;
        var hasFilters = false;
        var checks = form.querySelectorAll('input[type="checkbox"]');
        for (var i = 0; i < checks.length; i++) {
            if (checks[i].checked) { hasFilters = true; break; }
        }
        if (!hasFilters) {
            var numbers = form.querySelectorAll('input[type="number"]');
            for (var j = 0; j < numbers.length; j++) {
                if (numbers[j].value !== '') { hasFilters = true; break; }
            }
        }
        if (!hasFilters && getSortValue() !== '') {
            hasFilters = true;
        }
        clearBtn.disabled = !hasFilters;
    }

    updateClearBtn();

    /* ---- Clear filters ---- */
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            var checks = form.querySelectorAll('input[type="checkbox"]');
            for (var i = 0; i < checks.length; i++) {
                checks[i].checked = false;
            }
            var numbers = form.querySelectorAll('input[type="number"]');
            for (var j = 0; j < numbers.length; j++) {
                numbers[j].value = '';
            }
            var hiddenQ = form.querySelector('input[name="q"]');
            if (hiddenQ) hiddenQ.parentNode.removeChild(hiddenQ);
            setSortValue('');
            updateClearBtn();
            applyFilters();
        });
    }

    /* ---- AJAX pagination ---- */
    function attachPaginationHandlers() {
        var pagLinks = contentDiv.querySelectorAll('.pagination a');
        for (var k = 0; k < pagLinks.length; k++) {
            pagLinks[k].addEventListener('click', function(e) {
                e.preventDefault();
                var href = this.getAttribute('href');

                window.history.replaceState({}, '', href);

                if (mainEl) mainEl.classList.add('productos-main--loading');

                var pageReq = new XMLHttpRequest();
                pageReq.open('GET', href, true);
                pageReq.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                pageReq.onload = function() {
                    if (pageReq.status >= 200 && pageReq.status < 400) {
                        contentDiv.innerHTML = pageReq.responseText;
                        attachPaginationHandlers();
                    }
                    if (mainEl) mainEl.classList.remove('productos-main--loading');
                };
                pageReq.onerror = function() {
                    if (mainEl) mainEl.classList.remove('productos-main--loading');
                };
                pageReq.send();
            });
        }
    }

    attachPaginationHandlers();

})();
