/**
 * Validación en tiempo real de formularios
 * Proporciona feedback inmediato al usuario antes de enviar el formulario
 */

(function() {
    'use strict';

    // Inicializar validación cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        initFormValidation();
        initLoadingStates();
    });

    /**
     * Inicializa la validación en tiempo real para todos los formularios
     */
    function initFormValidation() {
        const forms = document.querySelectorAll('form[data-validate="true"]');
        
        forms.forEach(function(form) {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(function(input) {
                // Validar al perder el foco
                input.addEventListener('blur', function() {
                    validateField(input);
                });
                
                // Validar mientras escribe (con debounce)
                let timeout;
                input.addEventListener('input', function() {
                    clearTimeout(timeout);
                    timeout = setTimeout(function() {
                        validateField(input);
                    }, 500);
                });
            });
            
            // Validar antes de enviar
            form.addEventListener('submit', function(e) {
                if (!validateForm(form)) {
                    e.preventDefault();
                    e.stopPropagation();
                    showFormError(form, 'Por favor, corrige los errores antes de enviar.');
                } else {
                    showLoadingState(form);
                }
            });
        });
    }

    /**
     * Valida un campo individual
     */
    function validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        const minLength = field.getAttribute('minlength');
        const maxLength = field.getAttribute('maxlength');
        const pattern = field.getAttribute('pattern');
        
        let isValid = true;
        let errorMessage = '';
        
        // Validar campo requerido
        if (required && !value) {
            isValid = false;
            errorMessage = 'Este campo es obligatorio.';
        }
        
        // Validar longitud mínima
        if (isValid && minLength && value.length < parseInt(minLength)) {
            isValid = false;
            errorMessage = `Debe tener al menos ${minLength} caracteres.`;
        }
        
        // Validar longitud máxima
        if (isValid && maxLength && value.length > parseInt(maxLength)) {
            isValid = false;
            errorMessage = `No debe exceder ${maxLength} caracteres.`;
        }
        
        // Validar email
        if (isValid && type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Por favor, ingresa un email válido.';
            }
        }
        
        // Validar patrón
        if (isValid && pattern && value) {
            const regex = new RegExp(pattern);
            if (!regex.test(value)) {
                isValid = false;
                errorMessage = field.getAttribute('data-pattern-message') || 'El formato no es válido.';
            }
        }
        
        // Actualizar UI
        updateFieldValidation(field, isValid, errorMessage);
        
        return isValid;
    }

    /**
     * Valida todo el formulario
     */
    function validateForm(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        let isFormValid = true;
        
        inputs.forEach(function(input) {
            if (!validateField(input)) {
                isFormValid = false;
            }
        });
        
        return isFormValid;
    }

    /**
     * Actualiza la UI del campo según su estado de validación
     */
    function updateFieldValidation(field, isValid, errorMessage) {
        // Remover clases anteriores
        field.classList.remove('is-valid', 'is-invalid');
        
        // Remover mensaje de error anterior
        const existingError = field.parentElement.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        if (field.value.trim() === '') {
            // Campo vacío - estado neutral
            return;
        }
        
        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            
            // Agregar mensaje de error
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = errorMessage;
            field.parentElement.appendChild(errorDiv);
        }
    }

    /**
     * Muestra un error general en el formulario
     */
    function showFormError(form, message) {
        // Remover error anterior
        const existingError = form.querySelector('.alert-danger');
        if (existingError) {
            existingError.remove();
        }
        
        // Crear nuevo mensaje de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        form.insertBefore(errorDiv, form.firstChild);
        
        // Scroll al error
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /**
     * Inicializa los estados de carga
     */
    function initLoadingStates() {
        // Mostrar loading overlay en enlaces y formularios
        document.querySelectorAll('a[data-loading="true"], form[data-loading="true"]').forEach(function(element) {
            element.addEventListener('click', function() {
                showLoadingOverlay();
            });
        });
        
        // Ocultar loading overlay cuando la página carga
        window.addEventListener('load', function() {
            hideLoadingOverlay();
        });
    }

    /**
     * Muestra el estado de carga para un formulario
     */
    function showLoadingState(form) {
        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            const originalText = submitButton.innerHTML;
            submitButton.dataset.originalText = originalText;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Enviando...';
        }
    }

    /**
     * Muestra el overlay de carga
     */
    function showLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('d-none');
        }
    }

    /**
     * Oculta el overlay de carga
     */
    function hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('d-none');
        }
    }

    // Exportar funciones para uso global
    window.FormValidation = {
        validateField: validateField,
        validateForm: validateForm,
        showLoadingOverlay: showLoadingOverlay,
        hideLoadingOverlay: hideLoadingOverlay
    };
})();





