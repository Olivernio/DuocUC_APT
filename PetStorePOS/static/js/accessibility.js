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
    
    // Los eventos de los botones se manejan en el template accessibility.html
    // para incluir actualización de UI y mensajes de confirmación
});