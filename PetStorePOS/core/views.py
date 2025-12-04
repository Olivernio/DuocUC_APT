from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
import logging
import requests

logger = logging.getLogger(__name__)


svg_img = """ <svg xmlns="http://www.w3.org/2000/svg" class="logo" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="logo" aria-hidden="true"><circle cx="11" cy="4" r="2"></circle><circle cx="18" cy="8" r="2"></circle><circle cx="20" cy="16" r="2"></circle><path d="M9 10a5 5 0 0 1 5 5v3.5a3.5 3.5 0 0 1-6.84 1.045Q6.52 17.48 4.46 16.84A3.5 3.5 0 0 1 5.5 10Z"></path></svg> """
svg_img_check = """ <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-check-big h-6 w-6 text-green-600 mt-1 flex-shrink-0" aria-hidden="true"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg> """

def home(request):
    contexto  = {
        "svg_img": svg_img,
        "svg_img_check": svg_img_check,
    }
    return render(request, "core/home.html", contexto)


@require_http_methods(["POST"])
@csrf_exempt  # Temporalmente deshabilitar CSRF para debugging
def chatbot(request):
    """
    Vista para manejar las peticiones del chatbot con Perplexity AI.
    """
    from django.conf import settings
    
    # Verificar que Perplexity esté configurado
    perplexity_enabled = getattr(settings, 'PERPLEXITY_ENABLED', False)
    if not perplexity_enabled:
        return JsonResponse({
            'success': False,
            'response': 'El chatbot no está configurado. Por favor configura tu API key de Perplexity en settings.py'
        })
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'response': 'Por favor escribe un mensaje.'
            })
        
        # Obtener información contextual de la página
        from catalog.models import Product, Category
        from adoption.models import Mascota, Especies
        
        # Obtener categorías de productos disponibles con sus nombres legibles
        categories_raw = list(Product.objects.filter(is_active=True).values_list('category', flat=True).distinct())
        categories_list = []
        for cat_code in set(categories_raw):
            try:
                cat_name = dict(Category.choices).get(cat_code, cat_code)
                # Convertir a string explícitamente para evitar problemas con objetos __proxy__
                categories_list.append(str(cat_name))
            except:
                categories_list.append(str(cat_code))
        categories_str = ', '.join(categories_list) if categories_list else 'Alimentos, Medicamentos, Accesorios'
        
        # Obtener información sobre adopciones
        mascotas_count = Mascota.objects.filter(Estado='Disponible').count()
        mascotas_por_especie = {}
        for especie_code, especie_name in Especies.choices:
            count = Mascota.objects.filter(Estado='Disponible', Especie=especie_code).count()
            if count > 0:
                # Convertir a string explícitamente
                mascotas_por_especie[str(especie_name)] = count
        
        # Obtener algunos productos destacados (primeros 5)
        productos_destacados = Product.objects.filter(is_active=True)[:5]
        productos_info = []
        for producto in productos_destacados:
            cat_name = dict(Category.choices).get(producto.category, producto.category)
            productos_info.append(f"- {producto.name} ({str(cat_name)})")
        productos_str = '\n   '.join(productos_info) if productos_info else 'Consulta nuestro catálogo completo en la sección "Productos"'
        
        # Crear el prompt del sistema contextualizado
        system_prompt = f"""Eres un asistente virtual EXCLUSIVO de PetStorePOS, una tienda de mascotas que también gestiona adopciones.

REGLAS ESTRICTAS:
1. SOLO responde preguntas relacionadas con PetStorePOS (productos, adopciones, servicios de la tienda, accesibilidad)
2. Si el usuario pregunta sobre otros temas (política, deportes, tecnología general, noticias, etc.), responde EXACTAMENTE:
   "Lo siento, solo puedo ayudarte con información sobre PetStorePOS. ¿Hay algo específico sobre nuestros productos o adopciones que te interese?"
3. NO uses información de internet para temas no relacionados con PetStorePOS
4. NO respondas preguntas generales que no sean sobre la tienda

INFORMACIÓN ACTUAL DE PETSTOREPOS:

PRODUCTOS:
- Categorías disponibles: {categories_str}
- Productos destacados:
   {productos_str}
- Puedes recomendar productos según el tipo de mascota (perro, gato, pequeñas mascotas)
- Todos nuestros productos están disponibles en la sección "Productos" del sitio

ADOPCIÓN:
- Mascotas disponibles: {mascotas_count}
- Distribución por especie: {', '.join([f'{str(k)}: {v}' for k, v in mascotas_por_especie.items()]) if mascotas_por_especie else 'Consulta la sección Adopción'}
- Proceso: 1) Explorar mascotas, 2) Completar solicitud, 3) Revisión (1-3 días), 4) Contacto, 5) Adopción
- Tiempo estimado: 3-5 días hábiles

ACCESIBILIDAD (MUY IMPORTANTE):
PetStorePOS tiene un sistema completo de accesibilidad implementado. Las características disponibles son:

1. MODOS DE VISUALIZACIÓN (disponibles en la página de Accesibilidad):
   - Modo Estándar: Visualización por defecto con colores y contrastes estándar
   - Alto Contraste: Aumenta el contraste entre texto y fondo para mejorar la legibilidad. Ideal para personas con baja visión
   - Modo Daltónicos: Ajusta los colores para mejorar la distinción. Optimizado para protanopia y deuteranopia. ESTE MODO SÍ ESTÁ DISPONIBLE en PetStorePOS

2. CONTROL DE TAMAÑO DE FUENTE:
   - Permite ajustar el tamaño del texto desde 80% hasta 150%
   - Los cambios se guardan automáticamente en el navegador
   - Se aplica inmediatamente en toda la página

3. CARACTERÍSTICAS DE ACCESIBILIDAD:
   - Navegación por Teclado: Todo el sitio es navegable usando solo el teclado
   - Lectores de Pantalla: Compatible con NVDA, JAWS y VoiceOver (etiquetas semánticas HTML5 y atributos ARIA)
   - Colores Accesibles: Paleta optimizada para daltónicos, enlaces no dependen solo del color
   - Texto Escalable: Hasta 150% sin pérdida de funcionalidad
   - Multilenguaje: Soporte completo para múltiples idiomas

4. ESTÁNDARES:
   - Cumple con WCAG 2.1 Nivel AA
   - Cumple con Section 508

IMPORTANTE: Si un usuario pregunta sobre el "Modo Daltónicos" o "Modo para daltónicos", debes informar que SÍ está disponible en PetStorePOS. Puede activarse desde la página de Accesibilidad (/accesibilidad/). El modo ajusta los colores para mejorar la distinción, especialmente para protanopia y deuteranopia.

SERVICIOS:
- Venta de productos para mascotas
- Centro de adopción responsable
- Asesoramiento sobre cuidado de mascotas
- Sistema completo de accesibilidad

INSTRUCCIONES DE RESPUESTA:
- Sé amigable pero profesional
- Responde en español
- Mantén respuestas breves (2-3 oraciones máximo)
- Si no sabes algo específico, di: "Te recomiendo revisar nuestra sección de [Productos/Adopción/Accesibilidad] o contactar directamente con nuestro equipo"
- Dirige a los usuarios a las secciones del sitio cuando sea apropiado
- Si preguntan sobre accesibilidad, menciona que pueden visitar /accesibilidad/ para configurar los modos"""
        
        # Llamar a la API de Perplexity
        try:
            perplexity_api_key = settings.PERPLEXITY_API_KEY
            perplexity_url = "https://api.perplexity.ai/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            # Modelos válidos de Perplexity según documentación oficial
            # https://docs.perplexity.ai/getting-started/models
            # Modelos Sonar disponibles:
            # - sonar: Fast, reliable answers with detailed research
            # - sonar-reasoning: Smart problem-solving with real-time evidence
            # - sonar-deep-research: Expert-level insights from hundreds of sources
            # Intentar modelos en orden de preferencia (del más económico al más costoso)
            models_to_try = [
                "sonar",                    # Modelo básico - rápido y confiable
                "sonar-reasoning",          # Modelo medio - resolución de problemas avanzada
                "sonar-deep-research",      # Modelo avanzado - investigación profunda
            ]
            
            last_error = None
            for model in models_to_try:
                try:
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        "max_tokens": 200,
                        "temperature": 0.7
                    }
                    
                    response = requests.post(perplexity_url, json=payload, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    result = response.json()
                    bot_response = result['choices'][0]['message']['content'].strip()
                    
                    logger.info(f'Perplexity modelo usado: {model}')
                    return JsonResponse({
                        'success': True,
                        'response': bot_response
                    })
                    
                except requests.exceptions.RequestException as model_error:
                    last_error = model_error
                    error_str = str(model_error)
                    
                    # Intentar obtener el mensaje de error de la respuesta
                    error_message = error_str
                    try:
                        if hasattr(model_error, 'response') and model_error.response is not None:
                            error_data = model_error.response.json() if model_error.response.content else {}
                            if 'error' in error_data:
                                error_message = error_data['error'].get('message', error_str)
                    except:
                        pass
                    
                    # Si el error es de modelo inválido, intentar el siguiente
                    if 'Invalid model' in error_message or 'invalid_model' in error_message.lower():
                        logger.warning(f'Modelo {model} no válido: {error_message}. Intentando siguiente...')
                        continue
                    else:
                        # Si es otro error (autenticación, cuota, etc.), lanzarlo inmediatamente
                        raise
            
            # Si todos los modelos fallaron por ser inválidos, lanzar el último error
            if last_error:
                raise last_error
            
        except requests.exceptions.RequestException as e:
            logger.error(f'Perplexity API Error: {str(e)}', exc_info=True)
            
            # Obtener detalles del error de la respuesta si está disponible
            error_details = str(e)
            try:
                if hasattr(e, 'response') and e.response is not None:
                    error_data = e.response.json() if e.response.content else {}
                    error_details = error_data.get('error', {}).get('message', str(e))
                    logger.error(f'Perplexity API Response: {error_data}')
            except Exception as parse_error:
                logger.error(f'Error parsing Perplexity response: {parse_error}')
            
            # Manejar errores específicos de Perplexity
            error_msg = f'Error al conectar con Perplexity: {error_details}'
            if '401' in str(e) or 'unauthorized' in str(e).lower():
                error_msg = 'Error de autenticación con Perplexity. Verifica tu API key en settings.py'
            elif '429' in str(e) or 'quota' in str(e).lower():
                error_msg = 'Cuota de Perplexity excedida. Verifica tu plan en https://www.perplexity.ai/settings'
            elif '404' in str(e) or 'not found' in str(e).lower():
                error_msg = 'Endpoint de Perplexity no encontrado. Verifica la URL de la API.'
            
            # En modo DEBUG, mostrar más detalles
            if settings.DEBUG:
                error_msg += f'\n\nDetalles técnicos: {error_details}'
            
            return JsonResponse({
                'success': False,
                'response': error_msg
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'response': 'Error al procesar la solicitud.'
        })
    except Exception as e:
        # Log del error completo para debugging
        logger.error(f'Chatbot Unexpected Error: {str(e)}', exc_info=True)
        
        # En modo DEBUG, mostrar el error real
        from django.conf import settings
        if settings.DEBUG:
            error_msg = f'Error inesperado: {str(e)}'
        else:
            error_msg = 'Ocurrió un error inesperado. Por favor intenta más tarde.'
        
        return JsonResponse({
            'success': False,
            'response': error_msg
        })


