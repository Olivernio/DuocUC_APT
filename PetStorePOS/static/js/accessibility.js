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
}

// ---- Asignar Eventos a los Botones ----
document.addEventListener('DOMContentLoaded', () => {
    
    const btnHighContrast = document.getElementById('btn-high-contrast');
    const btnColorblind = document.getElementById('btn-colorblind'); // <-- Nuevo botón
    const btnDefault = document.getElementById('btn-default-mode');

    if (btnDefault) {
        btnDefault.addEventListener('click', () => {
            setAccessibilityMode('default');
        });
    }

    if (btnHighContrast) {
        btnHighContrast.addEventListener('click', () => {
            setAccessibilityMode('high-contrast');
        });
    }

    // --- Añade esto ---
    if (btnColorblind) {
        btnColorblind.addEventListener('click', () => {
            setAccessibilityMode('colorblind-mode');
        });
    }
    // --- Fin de lo añadido ---
});