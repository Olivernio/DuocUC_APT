// PetStorePOS/static/js/accessibility.js

/**
 * Aplica un modo de accesibilidad al sitio.
 * Guarda la preferencia en localStorage.
 * @param {string} mode - 'default', 'high-contrast', 'colorblind-mode', o 'dark-mode'
 */
function setAccessibilityMode(mode) {
    const root = document.documentElement; // El tag <html>

    // Limpia modos anteriores
    root.classList.remove('high-contrast');
    root.classList.remove('colorblind-mode');
    root.classList.remove('dark-mode');
    
    // Aplica el modo seleccionado
    if (mode === 'high-contrast') {
        root.classList.add('high-contrast');
        localStorage.setItem('accessibilityMode', 'high-contrast');
        
        // Sobrescribir estilos inline de degradado en páginas de login/register - FORZAR
        function forceBlackBackground() {
            // Forzar body y html - usar múltiples métodos para asegurar que funcione
            document.documentElement.style.setProperty('background', '#000000', 'important');
            document.documentElement.style.setProperty('background-color', '#000000', 'important');
            document.documentElement.style.setProperty('background-image', 'none', 'important');
            document.documentElement.style.removeProperty('background-attachment');
            document.documentElement.style.removeProperty('background-size');
            document.documentElement.style.removeProperty('background-position');
            document.documentElement.style.removeProperty('background-repeat');
            
            document.body.style.setProperty('background', '#000000', 'important');
            document.body.style.setProperty('background-color', '#000000', 'important');
            document.body.style.setProperty('background-image', 'none', 'important');
            document.body.style.removeProperty('background-attachment');
            document.body.style.removeProperty('background-size');
            document.body.style.removeProperty('background-position');
            document.body.style.removeProperty('background-repeat');
            
            // También sobrescribir cualquier contenedor con degradado
            const gradientElements = document.querySelectorAll('.gradient-left, .gradient-bg');
            gradientElements.forEach(el => {
                el.style.setProperty('background', '#000000', 'important');
                el.style.setProperty('background-color', '#000000', 'important');
                el.style.setProperty('background-image', 'none', 'important');
            });
        }
        
        if (document.body.classList.contains('login-page') || document.documentElement.classList.contains('login-page')) {
            forceBlackBackground();
            // Ejecutar múltiples veces para asegurar que se aplique después de otros scripts
            setTimeout(forceBlackBackground, 50);
            setTimeout(forceBlackBackground, 200);
            setTimeout(forceBlackBackground, 500);
            setTimeout(forceBlackBackground, 1000);
        }

    } else if (mode === 'colorblind-mode') {
        root.classList.add('colorblind-mode');
        localStorage.setItem('accessibilityMode', 'colorblind-mode');

    } else if (mode === 'dark-mode') {
        root.classList.add('dark-mode');
        localStorage.setItem('accessibilityMode', 'dark-mode');
        
        // Asegurar que el modo oscuro se aplique correctamente
        document.body.style.setProperty('background-color', '#0a0a0a', 'important');
        document.body.style.setProperty('color', '#ffffff', 'important');

    } else {
        // Modo 'default' o normal
        root.classList.remove('dark-mode');
        localStorage.setItem('accessibilityMode', 'default');
        // Restaurar estilos por defecto
        document.body.style.removeProperty('background-color');
        document.body.style.removeProperty('color');
    }
    
    // Aplicar tamaño de fuente guardado
    const savedFontSize = localStorage.getItem('fontSize') || '1.0';
    if (savedFontSize) {
        document.documentElement.style.fontSize = savedFontSize + 'rem';
    }
}

// Función helper para modo oscuro
function setDarkMode() {
    setAccessibilityMode('dark-mode');
}

// Función helper para desactivar modo oscuro
function removeDarkMode() {
    setAccessibilityMode('default');
}

// Toggle modo oscuro
function toggleDarkMode() {
    const root = document.documentElement;
    const isDarkMode = root.classList.contains('dark-mode');
    
    if (isDarkMode) {
        removeDarkMode();
    } else {
        setDarkMode();
    }
    
    // Actualizar icono del botón si existe
    updateDarkModeButton();
}

// Actualizar icono del botón de modo oscuro
function updateDarkModeButton() {
    const root = document.documentElement;
    const isDarkMode = root.classList.contains('dark-mode');
    const darkModeButtons = document.querySelectorAll('[data-dark-mode-toggle]');
    
    darkModeButtons.forEach(btn => {
        const icon = btn.querySelector('i');
        if (icon) {
            if (isDarkMode) {
                icon.classList.remove('bi-moon');
                icon.classList.add('bi-sun');
                btn.setAttribute('aria-label', 'Desactivar modo oscuro');
            } else {
                icon.classList.remove('bi-sun');
                icon.classList.add('bi-moon');
                btn.setAttribute('aria-label', 'Activar modo oscuro');
            }
        }
    });
}

// ---- Aplicar preferencias guardadas al cargar la página ----
document.addEventListener('DOMContentLoaded', () => {
    // Aplicar modo guardado
    const savedMode = localStorage.getItem('accessibilityMode');
    if (savedMode) {
        setAccessibilityMode(savedMode);
    }
    
    // Actualizar botones de modo oscuro
    updateDarkModeButton();
    
    // Agregar event listeners a los botones de toggle
    const darkModeButtons = document.querySelectorAll('[data-dark-mode-toggle]');
    darkModeButtons.forEach(btn => {
        btn.addEventListener('click', toggleDarkMode);
    });
    
    // Aplicar tamaño de fuente guardado
    const savedFontSize = localStorage.getItem('fontSize');
    if (savedFontSize) {
        document.documentElement.style.fontSize = savedFontSize + 'rem';
    }
    
    // Si está en modo alto contraste, asegurar que los estilos inline se sobrescriban
    // después de que se carguen los scripts de login
    if (savedMode === 'high-contrast') {
        function forceBlackBg() {
            // Forzar body y html - eliminar TODAS las propiedades de background
            document.documentElement.style.setProperty('background', '#000000', 'important');
            document.documentElement.style.setProperty('background-color', '#000000', 'important');
            document.documentElement.style.setProperty('background-image', 'none', 'important');
            document.documentElement.style.removeProperty('background-attachment');
            document.documentElement.style.removeProperty('background-size');
            document.documentElement.style.removeProperty('background-position');
            document.documentElement.style.removeProperty('background-repeat');
            
            document.body.style.setProperty('background', '#000000', 'important');
            document.body.style.setProperty('background-color', '#000000', 'important');
            document.body.style.setProperty('background-image', 'none', 'important');
            document.body.style.removeProperty('background-attachment');
            document.body.style.removeProperty('background-size');
            document.body.style.removeProperty('background-position');
            document.body.style.removeProperty('background-repeat');
            
            // También sobrescribir cualquier contenedor con degradado
            const gradientElements = document.querySelectorAll('.gradient-left, .gradient-bg');
            gradientElements.forEach(el => {
                el.style.setProperty('background', '#000000', 'important');
                el.style.setProperty('background-color', '#000000', 'important');
                el.style.setProperty('background-image', 'none', 'important');
            });
        }
        
        if (document.body.classList.contains('login-page') || document.documentElement.classList.contains('login-page')) {
            forceBlackBg();
            // Ejecutar múltiples veces para asegurar que se aplique después de otros scripts
            setTimeout(forceBlackBg, 100);
            setTimeout(forceBlackBg, 300);
            setTimeout(forceBlackBg, 600);
            setTimeout(forceBlackBg, 1000);
        }
    }
    
    // Los eventos de los botones se manejan en el template accessibility.html
    // para incluir actualización de UI y mensajes de confirmación
});

// Observar cambios en el modo de accesibilidad
window.addEventListener('storage', function(e) {
    if (e.key === 'accessibilityMode') {
        const newMode = localStorage.getItem('accessibilityMode');
        setAccessibilityMode(newMode);
    }
});