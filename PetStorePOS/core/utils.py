import requests
import re
from django.core.cache import cache
import time

def traducir_texto(texto, lang_destino, add_p_tags=False):
    """
    Traduce texto usando MyMemory API y lo guarda en caché.
    Acorta el texto a 490 caracteres para respetar el límite de la API.
    """
    if not texto or not texto.strip():
        return texto 

    lang_par = f"es|{lang_destino}"
    
    texto_limpio = re.sub(r'<[^>]+>', ' ', texto).strip()
    
    texto_acortado = texto_limpio[:490]
    if len(texto_limpio) > 490:
        texto_acortado += " (...)"

    cache_key = f"translation_{hash(texto_acortado)}_{lang_destino}_{add_p_tags}"
    
    traduccion_cacheada = cache.get(cache_key)
    if traduccion_cacheada:
        return traduccion_cacheada # ¡La encontramos en el caché!

    print(f"--- LLAMANDO A API MYMEMORY (DESDE CORE.UTILS) PARA: {texto_acortado[:30]}...") 
    try:
        api_url = "https://api.mymemory.translated.net/get"
        parametros = {'q': texto_acortado, 'langpair': lang_par}
        
        response = requests.get(api_url, params=parametros, timeout=10)
        time.sleep(1.1) # Pausa de 1.1s para evitar error 429
        response.raise_for_status() 
        data = response.json()
        
        if data.get('responseStatus') == 200:
            # --- INICIO DE LA CORRECCIÓN DEL NAMEERROR ---
            traduccion = data['responseData']['translatedText'] # Variable definida
            
            if add_p_tags:
                # Si se piden (para Adopción), reconstruimos los párrafos
                parrafos = traduccion.split('\n')
                resultado_final = "".join(f"<p>{p.strip()}</p>" for p in parrafos if p.strip())
            else:
                # Si no (para Catálogo), devolvemos el texto plano
                resultado_final = traduccion
            
            cache.set(cache_key, resultado_final, 60 * 60 * 24) # Guardar por 24 horas
            return resultado_final
            # --- FIN DE LA CORRECCIÓN DEL NAMEERROR ---
        else:
            print(f"Error de MyMemory API: {data.get('responseDetails')}")
            return texto # Devolver original si la API da error
            
    except requests.exceptions.RequestException as e:
        print(f"Error de red al llamar a MyMemory: {e}")
        return texto # Devolver original si falla la conexión