// PetStorePOS/static/js/accessibility.js

/**
 * Aplica un modo de accesibilidad al sitio.
 * Guarda la preferencia en localStorage.
 * @param {string} mode - 'default', 'high-contrast', o 'colorblind-mode'
 */
function setAccessibilityMode(mode) {
    const root = document.documentElement; // El tag <html>

    // Limpia modos anteriores
    root.classList.remove('high-contrast');
    root.classList.remove('colorblind-mode');
    
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
            
            // No usar MutationObserver aquí para evitar bucles infinitos
            // Se maneja en los templates individuales con protección
        }

    } else if (mode === 'colorblind-mode') {
        root.classList.add('colorblind-mode');
        localStorage.setItem('accessibilityMode', 'colorblind-mode');

    } else {
        // Modo 'default' o normal
        localStorage.setItem('accessibilityMode', 'default');
    }
    
    // Aplicar tamaño de fuente guardado
    const savedFontSize = localStorage.getItem('fontSize') || '1.0';
    if (savedFontSize) {
        document.documentElement.style.fontSize = savedFontSize + 'rem';
    }
}

// ---- Aplicar preferencias guardadas al cargar la página ----
document.addEventListener('DOMContentLoaded', () => {
    // Aplicar modo guardado
    const savedMode = localStorage.getItem('accessibilityMode');
    if (savedMode) {
        setAccessibilityMode(savedMode);
    }
    
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
            
            // No usar MutationObserver ni setInterval aquí para evitar bucles infinitos
            // Los cambios se aplican mediante setTimeout controlados solo al inicio
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