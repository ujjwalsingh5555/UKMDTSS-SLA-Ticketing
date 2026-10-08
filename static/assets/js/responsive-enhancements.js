(function () {
    'use strict';

    function ready(fn) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            fn();
        }
    }

    ready(function () {
        var sidebar = document.getElementById('sidebar');

        // Automatically make ordinary Bootstrap tables scroll safely on phones.
        document.querySelectorAll('table.table').forEach(function (table) {
            if (table.closest('.table-responsive') || table.closest('.dataTable-container')) return;
            var wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        });

        if (!sidebar) return;

        var backdrop = document.createElement('div');
        backdrop.className = 'mazer-sidebar-backdrop';
        backdrop.setAttribute('aria-hidden', 'true');
        document.body.appendChild(backdrop);

        function syncSidebarState() {
            var isMobile = window.innerWidth < 1200;
            var isOpen = isMobile && sidebar.classList.contains('active');
            document.body.classList.toggle('mazer-sidebar-open', isOpen);
        }

        new MutationObserver(syncSidebarState).observe(sidebar, {
            attributes: true,
            attributeFilter: ['class']
        });

        backdrop.addEventListener('click', function () {
            sidebar.classList.remove('active');
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && window.innerWidth < 1200) {
                sidebar.classList.remove('active');
            }
        });

        window.addEventListener('resize', syncSidebarState, { passive: true });
        document.querySelectorAll('.burger-btn, .sidebar-hide').forEach(function (control) {
            control.addEventListener('click', function () {
                window.setTimeout(syncSidebarState, 0);
            });
        });

        syncSidebarState();
    });
})();
