/**
 * JavaScript para manejar favoritos con AJAX
 * Permite agregar/quitar favoritos sin recargar la página
 */

document.addEventListener('DOMContentLoaded', function() {
    // Obtener todos los botones de favorito
    const favoriteButtons = document.querySelectorAll('[id^="favorite-btn-"]');
    
    favoriteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Prevenir navegación normal
            
            const url = this.getAttribute('href');
            const button = this;
            const icon = button.querySelector('i');
            const originalText = button.innerHTML;
            
            // Mostrar estado de carga
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-hourglass-split"></i> Cargando...';
            
            // Obtener CSRF token
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            
            // Hacer petición AJAX
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken') || ''
                }
            })
            .then(response => response.json())
            .then(data => {
                // Actualizar botón según respuesta
                if (data.is_favorite) {
                    button.classList.remove('btn-outline-danger');
                    button.classList.add('btn-danger');
                    icon.classList.remove('bi-heart');
                    icon.classList.add('bi-heart-fill');
                    button.innerHTML = '<i class="bi bi-heart-fill"></i> En Favoritos';
                    button.setAttribute('title', 'Quitar de favoritos');
                } else {
                    button.classList.remove('btn-danger');
                    button.classList.add('btn-outline-danger');
                    icon.classList.remove('bi-heart-fill');
                    icon.classList.add('bi-heart');
                    button.innerHTML = '<i class="bi bi-heart"></i> Agregar a Favoritos';
                    button.setAttribute('title', 'Agregar a favoritos');
                }
                
                button.disabled = false;
                
                // Mostrar mensaje de éxito (opcional)
                if (data.message) {
                    // Puedes usar toast notifications aquí si las tienes
                    console.log(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                button.innerHTML = originalText;
                button.disabled = false;
                alert('Ocurrió un error al actualizar favoritos. Por favor, recarga la página.');
            });
        });
    });
});

