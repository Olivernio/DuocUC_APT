# 📋 Guía Completa de Migración - PetCare

Esta guía te ayudará a implementar todas las funcionalidades creadas en este proyecto en tu otro proyecto, paso a paso y en el orden correcto para evitar errores.

---

## 📦 **PASO 1: Preparación y Dependencias**

### 1.1 Instalar dependencias necesarias

```bash
pip install django-bootstrap5 django-formtools requests django-widget-tweaks django-recaptcha openai
```

O agrega a tu `requirements.txt`:
```
asgiref==3.9.1
Django==5.2.6
pillow==11.3.0
sqlparse==0.5.3
tzdata==2025.2
django-bootstrap5==25.2
django-formtools==2.5.1
requests==2.32.5
django-widget-tweaks
django-recaptcha
openai>=2.8.0
```

### 1.2 Verificar estructura de apps

Asegúrate de tener estas apps en tu proyecto:
- `accounts` (usuarios y perfiles)
- `catalog` (productos)
- `orders` (pedidos)
- `cart` (carrito)
- `adoption` (adopciones)
- `dashboard` (panel de administración)
- `core` (vistas principales)

---

## 📦 **PASO 2: Modelos (Base de Datos)**

### 2.1 Modificar `accounts/models.py`

**Agregar al modelo `UserProfile`:**
```python
favorite_products = models.ManyToManyField(
    'catalog.Product',
    related_name='favorited_by',    
    blank=True,
    verbose_name=_("Productos Favoritos")
)
```

**Agregar modelo `Notification`:**
```python
class NotificationType(models.TextChoices):
    ORDER_CREATED = "ORDER_CREATED", _("Orden Creada")
    ORDER_UPDATED = "ORDER_UPDATED", _("Orden Actualizada")
    REVIEW_APPROVED = "REVIEW_APPROVED", _("Reseña Aprobada")
    ADOPTION_APPROVED = "ADOPTION_APPROVED", _("Adopción Aprobada")
    GENERAL = "GENERAL", _("General")

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.GENERAL)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
```

### 2.2 Modificar `catalog/models.py`

**Agregar modelo `ProductReview`:**
```python
class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Agregar métodos al modelo `Product`:**
```python
def get_average_rating(self):
    from django.db.models import Avg
    avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
    return round(avg, 1) if avg else 0

def get_total_reviews(self):
    return self.reviews.filter(is_approved=True).count()
```

### 2.3 Modificar `orders/models.py`

**Agregar modelos de cupones:**
```python
class DiscountType(models.TextChoices):
    PERCENTAGE = "PERCENTAGE", _("Porcentaje")
    FIXED = "FIXED", _("Fijo")

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def calculate_discount(self, total):
        if self.discount_type == DiscountType.PERCENTAGE:
            discount = (total * self.discount_value) / 100
        else:
            discount = min(self.discount_value, total)
        return discount, total - discount
    
    def apply(self):
        self.used_count += 1
        self.save()

class OrderCoupon(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='applied_coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
```

### 2.4 Ejecutar migraciones

```bash
python manage.py makemigrations accounts
python manage.py makemigrations catalog
python manage.py makemigrations orders
python manage.py migrate
```

---

## 📦 **PASO 3: Utilidades y Helpers**

### 3.1 Crear `accounts/utils.py`

```python
from .models import Notification, NotificationType

def notify_order_created(user, order):
    Notification.objects.create(
        user=user,
        type=NotificationType.ORDER_CREATED,
        title=f"Orden #{order.order_number} creada",
        message=f"Tu orden ha sido creada exitosamente. Total: ${order.total}",
        link=f"/orders/pedido/{order.id}/"
    )

def notify_review_approved(user, review):
    Notification.objects.create(
        user=user,
        type=NotificationType.REVIEW_APPROVED,
        title="Reseña aprobada",
        message=f"Tu reseña para {review.product.name} ha sido aprobada.",
        link=f"/catalog/producto/{review.product.id}/"
    )
```

### 3.2 Crear `accounts/templatetags/accounts_tags.py`

```python
from django import template
from django.db.utils import OperationalError

register = template.Library()

@register.simple_tag
def get_user_profile(user):
    try:
        from .models import UserProfile
        return UserProfile.objects.get_or_create(user=user)[0]
    except OperationalError:
        return None

@register.simple_tag
def get_unread_notifications_count(user):
    try:
        from .models import Notification
        return Notification.objects.filter(user=user, is_read=False).count()
    except OperationalError:
        return 0
```

**Crear `accounts/templatetags/__init__.py`** (vacío)

### 3.3 Crear `core/templatetags/breadcrumbs.py`

```python
from django import template

register = template.Library()

@register.inclusion_tag('core/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, *items):
    return {'items': items}
```

**Crear `core/templatetags/__init__.py`** (vacío)

### 3.4 Crear `core/utils.py`

```python
from django.core.cache import cache
from django.db.models import Sum, Count, Avg
from django.utils.translation import gettext_lazy as _

def get_dashboard_stats():
    cache_key = 'dashboard_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        from orders.models import Order
        from catalog.models import Product
        from adoption.models import Mascota
        
        stats = {
            'total_orders': Order.objects.count(),
            'total_revenue': Order.objects.aggregate(total=Sum('total'))['total'] or 0,
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_pets': Mascota.objects.filter(Estado='Disponible').count(),
        }
        cache.set(cache_key, stats, 300)  # Cache por 5 minutos
    
    return stats
```

---

## 📦 **PASO 4: Formularios**

### 4.1 Crear `catalog/forms.py` (si no existe)

```python
from django import forms
from .models import Product, ProductReview
from orders.models import OrderItem

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError("La calificación debe estar entre 1 y 5.")
        return rating
```

### 4.2 Modificar `orders/forms.py`

**Agregar `CouponForm`:**
```python
from django import forms
from django.db.utils import OperationalError

class CouponForm(forms.Form):
    coupon_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de cupón'})
    )
    
    def clean_coupon_code(self):
        code = self.cleaned_data.get('coupon_code')
        if not code:
            return None
        
        try:
            from .models import Coupon
            from django.utils import timezone
            
            coupon = Coupon.objects.get(
                code=code.upper(),
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_until__gte=timezone.now()
            )
            
            if coupon.used_count >= coupon.max_uses:
                raise forms.ValidationError("Este cupón ha alcanzado su límite de usos.")
            
            return coupon
        except OperationalError:
            return None
        except Coupon.DoesNotExist:
            raise forms.ValidationError("Código de cupón inválido o expirado.")
```

---

## 📦 **PASO 5: Vistas**

### 5.1 Modificar `accounts/views.py`

**Agregar vistas de favoritos:**
```python
@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if product in user_profile.favorite_products.all():
        user_profile.favorite_products.remove(product)
        is_favorite = False
    else:
        user_profile.favorite_products.add(product)
        is_favorite = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite})
    
    return redirect('catalog:product_list')

@login_required
def favorites_list(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    favorites = user_profile.favorite_products.filter(is_active=True)
    
    context = {
        'favorites': favorites,
        'favorites_count': favorites.count(),
    }
    return render(request, 'accounts/favorites.html', context)
```

**Agregar vistas de notificaciones:**
```python
@login_required
def notifications_list(request):
    from django.db.utils import OperationalError
    try:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        unread_count = notifications.filter(is_read=False).count()
    except OperationalError:
        notifications = []
        unread_count = 0
    
    return render(request, 'accounts/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })

@login_required
def mark_notification_read(request, notification_id):
    from django.db.utils import OperationalError
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, "Notificación marcada como leída")
        return redirect('accounts:notifications')
    except OperationalError:
        return redirect('home')
```

**Modificar `profile_view` para incluir pestañas:**
```python
@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    tab = request.GET.get('tab', 'perfil')
    
    # Obtener datos reales
    from orders.models import Order
    from catalog.models import ProductReview
    from adoption.models import AdoptionRequest
    from django.db.models import Sum, Count
    from django.core.paginator import Paginator
    
    user_orders = Order.objects.filter(user=request.user).count()
    total_spent = Order.objects.filter(user=request.user).aggregate(total=Sum('total'))['total'] or 0
    adoptions = AdoptionRequest.objects.filter(email=request.user.email).count()
    reviews = ProductReview.objects.filter(user=request.user, is_approved=True).count()
    
    # Datos para las pestañas
    orders_list = []
    if tab == 'pedidos':
        orders_list = Order.objects.filter(user=request.user).order_by('-created_at')
        paginator = Paginator(orders_list, 10)
        page_number = request.GET.get('page')
        orders_list = paginator.get_page(page_number)
    
    context = {
        "user": request.user,
        "user_orders": user_orders,
        "total_spent": total_spent,
        "adoptions": adoptions,
        "reviews": reviews,
        "active_tab": tab,
        "orders_list": orders_list,
    }
    return render(request, "accounts/profile.html", context)
```

### 5.2 Modificar `catalog/views.py`

**Agregar vista de detalle de producto:**
```python
class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Reseñas aprobadas
        context['reviews'] = product.reviews.filter(is_approved=True).order_by('-created_at')
        context['average_rating'] = product.get_average_rating()
        context['total_reviews'] = product.get_total_reviews()
        
        # Verificar si el usuario puede reseñar
        context['can_review'] = False
        if self.request.user.is_authenticated:
            from orders.models import OrderItem
            has_purchased = OrderItem.objects.filter(
                order__user=self.request.user,
                product=product
            ).exists()
            has_reviewed = product.reviews.filter(user=self.request.user).exists()
            context['can_review'] = has_purchased and not has_reviewed
        
        return context

@login_required
def create_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Verificar que el usuario haya comprado el producto
    from orders.models import OrderItem
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exists()
    
    if not has_purchased:
        messages.error(request, "Debes haber comprado este producto para poder reseñarlo.")
        return redirect('catalog:product_detail', pk=product.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Tu reseña ha sido enviada y será revisada.")
            return redirect('catalog:product_detail', pk=product.id)
    else:
        form = ReviewForm()
    
    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'form': form,
    })
```

### 5.3 Modificar `orders/views.py`

**Modificar `checkout_view` para incluir cupones:**
```python
@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if cart.items.count() == 0:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('cart:cart_detail')
    
    # Formularios
    form = CheckoutForm(request.POST or None)
    coupon_form = CouponForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        discount_amount = 0
        applied_coupon = None
        
        # Validar cupón
        if coupon_form.is_valid():
            applied_coupon = coupon_form.cleaned_data.get('coupon_code')
        
        try:
            with transaction.atomic():
                total = sum(item.product.price * item.quantity for item in cart.items.all())
                
                if applied_coupon:
                    discount_amount, total = applied_coupon.calculate_discount(total)
                
                order = Order.objects.create(
                    user=request.user,
                    status=OrderStatus.PENDING,
                    shipping_address=form.cleaned_data['shipping_address'],
                    shipping_city=form.cleaned_data['shipping_city'],
                    shipping_postal_code=form.cleaned_data.get('shipping_postal_code', ''),
                    notes=form.cleaned_data.get('notes', ''),
                    total=total
                )
                
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.save()
                
                if applied_coupon:
                    OrderCoupon.objects.create(
                        order=order,
                        coupon=applied_coupon,
                        discount_amount=discount_amount
                    )
                    applied_coupon.apply()
                
                cart.items.all().delete()
            
            # Crear notificación
            try:
                from accounts.utils import notify_order_created
                notify_order_created(request.user, order)
            except:
                pass
            
            messages.success(request, f"¡Orden creada exitosamente! Número: {order.order_number}")
            return redirect('orders:order_detail', order_id=order.id)
            
        except Exception as e:
            messages.error(request, "Ocurrió un error al procesar tu orden.")
            if settings.DEBUG:
                print(f"Error en checkout: {e}")
    
    context = {
        'form': form,
        'coupon_form': coupon_form,
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)
```

### 5.4 Modificar `core/views.py`

**Agregar vista de chatbot:**
```python
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@csrf_exempt
def chatbot(request):
    from django.conf import settings
    
    perplexity_enabled = getattr(settings, 'PERPLEXITY_ENABLED', False)
    if not perplexity_enabled:
        return JsonResponse({
            'success': False,
            'response': 'El chatbot no está configurado.'
        })
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'response': 'Por favor escribe un mensaje.'
            })
        
        # Obtener información contextual
        from catalog.models import Product, Category
        from adoption.models import Mascota, Especies
        
        categories_raw = list(Product.objects.filter(is_active=True).values_list('category', flat=True).distinct())
        categories_list = []
        for cat_code in set(categories_raw):
            try:
                cat_name = dict(Category.choices).get(cat_code, cat_code)
                categories_list.append(str(cat_name))
            except:
                categories_list.append(str(cat_code))
        categories_str = ', '.join(categories_list) if categories_list else 'Alimentos, Medicamentos, Accesorios'
        
        mascotas_count = Mascota.objects.filter(Estado='Disponible').count()
        
        system_prompt = f"""Eres un asistente virtual EXCLUSIVO de PetCare.

REGLAS ESTRICTAS:
1. SOLO responde preguntas relacionadas con PetCare
2. Si preguntan sobre otros temas, di: "Lo siento, solo puedo ayudarte con información sobre PetCare."

INFORMACIÓN DE PETCARE:
- Categorías: {categories_str}
- Mascotas disponibles: {mascotas_count}
- Servicios: Productos, Adopciones, Accesibilidad

Responde en español, sé breve (2-3 oraciones)."""
        
        # Llamar a Perplexity
        perplexity_api_key = settings.PERPLEXITY_API_KEY
        perplexity_url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        models_to_try = ["sonar", "sonar-reasoning", "sonar-deep-research"]
        
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
                
                return JsonResponse({
                    'success': True,
                    'response': bot_response
                })
            except:
                continue
        
        return JsonResponse({
            'success': False,
            'response': 'Error al conectar con el servicio.'
        })
        
    except Exception as e:
        logger.error(f'Chatbot error: {str(e)}', exc_info=True)
        return JsonResponse({
            'success': False,
            'response': 'Ocurrió un error. Por favor intenta más tarde.'
        })
```

---

## 📦 **PASO 6: URLs**

### 6.1 Modificar `accounts/urls.py`

```python
urlpatterns = [
    # ... URLs existentes ...
    path('favoritos/', views.favorites_list, name='favorites'),
    path('favoritos/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('notificaciones/', views.notifications_list, name='notifications'),
    path('notificaciones/<int:notification_id>/marcar-leida/', views.mark_notification_read, name='mark_notification_read'),
    path('notificaciones/marcar-todas-leidas/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
```

### 6.2 Modificar `catalog/urls.py`

```python
urlpatterns = [
    # ... URLs existentes ...
    path('producto/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('producto/<int:product_id>/reseña/', views.create_review, name='create_review'),
]
```

### 6.3 Modificar `djangocrud/urls.py` (o tu archivo principal de URLs)

```python
from core.views import chatbot

urlpatterns = [
    # ... URLs existentes ...
    path("chatbot/", chatbot, name="chatbot"),
]
```

---

## 📦 **PASO 7: Configuración (settings.py)**

### 7.1 Agregar configuración de chatbot

```python
import os

# Chatbot Configuration - Perplexity
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY', '')
PERPLEXITY_ENABLED = bool(PERPLEXITY_API_KEY)
```

### 7.2 Agregar context processor

**Crear `core/context_processors.py`:**
```python
from django.conf import settings

def openai_chatbot(request):
    return {
        'OPENAI_ENABLED': getattr(settings, 'PERPLEXITY_ENABLED', False),
    }
```

**En `settings.py`, agregar a `TEMPLATES['OPTIONS']['context_processors']`:**
```python
TEMPLATES = [
    {
        # ...
        'OPTIONS': {
            'context_processors': [
                # ... existentes ...
                'core.context_processors.openai_chatbot',
            ],
        },
    },
]
```

### 7.3 Configurar caché (opcional)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

---

## 📦 **PASO 8: Templates**

### 8.1 Modificar `templates/base.html`

**Agregar dropdown de usuario:**
- Buscar la sección del navbar donde está el usuario
- Reemplazar con el dropdown que incluye: Dashboard (si es staff), Mi Cuenta, Favoritos, Notificaciones, Cerrar Sesión

**Agregar widget de chatbot:**
- Al final del body, antes de `</body>`
- Incluir el HTML del widget y el JavaScript

### 8.2 Crear templates nuevos

**`templates/accounts/favorites.html`**
**`templates/accounts/notifications.html`**
**`templates/catalog/product_detail.html`**
**`templates/core/breadcrumbs.html`**

### 8.3 Modificar templates existentes

**`templates/accounts/profile.html`**: Agregar pestañas (Perfil, Pedidos, Mascotas, Reseñas)
**`templates/orders/checkout.html`**: Agregar sección de cupones
**`templates/orders/order_detail.html`**: Mostrar descuentos aplicados

---

## 📦 **PASO 9: Archivos Estáticos**

### 9.1 Crear `static/js/accessibility.js`
### 9.2 Crear `static/css/accessibility.css`
### 9.3 Crear `static/js/form-validation.js`

---

## 📦 **PASO 10: Admin**

### 10.1 Modificar `accounts/admin.py`

```python
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'title', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__email', 'title', 'message']
```

### 10.2 Modificar `catalog/admin.py`

```python
from .models import ProductReview

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reseñas aprobadas.")
    approve_reviews.short_description = "Aprobar reseñas seleccionadas"
```

### 10.3 Modificar `orders/admin.py`

```python
from .models import Coupon, OrderCoupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'used_count', 'max_uses', 'is_active']
    list_filter = ['is_active', 'discount_type']
    search_fields = ['code']

@admin.register(OrderCoupon)
class OrderCouponAdmin(admin.ModelAdmin):
    list_display = ['order', 'coupon', 'discount_amount']
```

---

## 📦 **PASO 11: Ejecutar Migraciones**

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📦 **PASO 12: Verificar y Probar**

1. ✅ Verificar que todas las migraciones se ejecutaron correctamente
2. ✅ Probar el sistema de favoritos
3. ✅ Probar las reseñas de productos
4. ✅ Probar las notificaciones
5. ✅ Probar los cupones en checkout
6. ✅ Probar el chatbot
7. ✅ Verificar el dropdown de usuario
8. ✅ Verificar las pestañas en "Mi Cuenta"

---

## ⚠️ **ORDEN CRÍTICO DE IMPLEMENTACIÓN**

**NO cambies el orden, o tendrás errores:**

1. **Primero**: Modelos (Paso 2)
2. **Segundo**: Migraciones (Paso 2.4)
3. **Tercero**: Utilidades (Paso 3)
4. **Cuarto**: Formularios (Paso 4)
5. **Quinto**: Vistas (Paso 5)
6. **Sexto**: URLs (Paso 6)
7. **Séptimo**: Settings (Paso 7)
8. **Octavo**: Templates (Paso 8)
9. **Noveno**: Estáticos (Paso 9)
10. **Décimo**: Admin (Paso 10)
11. **Onceavo**: Migraciones finales (Paso 11)

---

## 📝 **NOTAS IMPORTANTES**

- **Siempre ejecuta migraciones después de modificar modelos**
- **Verifica que los imports sean correctos**
- **Asegúrate de tener las mismas apps instaladas**
- **Revisa que los nombres de modelos coincidan**
- **Prueba cada funcionalidad después de implementarla**

---

## 🆘 **Si algo falla**

1. Revisa los logs del servidor: `python manage.py runserver`
2. Verifica las migraciones: `python manage.py showmigrations`
3. Revisa los imports en cada archivo
4. Asegúrate de que todas las dependencias estén instaladas
5. Verifica que los templates existan en las rutas correctas

---

## 📦 **PASO 13: CHATBOT CON PERPLEXITY AI** (Agregado después de Fase 4)

### 13.1 Instalar dependencia adicional

```bash
pip install requests
```

O agregar a `requirements.txt`:
```
requests==2.32.5
```

### 13.2 Configurar API Key en `settings.py`

```python
import os

# Chatbot Configuration - Perplexity
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY', '')
PERPLEXITY_ENABLED = bool(PERPLEXITY_API_KEY)
```

**Nota:** Para obtener tu API key de Perplexity:
1. Ve a https://www.perplexity.ai/settings/api
2. Copia tu API key
3. Configúrala como variable de entorno o directamente en settings.py (solo para desarrollo)

### 13.3 Crear Context Processor

**Crear `core/context_processors.py`:**
```python
from django.conf import settings

def openai_chatbot(request):
    """
    Hace disponible la configuración del chatbot en todos los templates.
    """
    return {
        'OPENAI_ENABLED': getattr(settings, 'PERPLEXITY_ENABLED', False),
    }
```

**En `settings.py`, agregar al contexto:**
```python
TEMPLATES = [
    {
        # ...
        'OPTIONS': {
            'context_processors': [
                # ... existentes ...
                'core.context_processors.openai_chatbot',
            ],
        },
    },
]
```

### 13.4 Crear vista del chatbot

**Modificar `core/views.py` - Agregar al final:**
```python
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@csrf_exempt
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
        system_prompt = f"""Eres un asistente virtual EXCLUSIVO de PetCare, una tienda de mascotas que también gestiona adopciones.

REGLAS ESTRICTAS:
1. SOLO responde preguntas relacionadas con PetCare (productos, adopciones, servicios de la tienda, accesibilidad)
2. Si el usuario pregunta sobre otros temas (política, deportes, tecnología general, noticias, etc.), responde EXACTAMENTE:
   "Lo siento, solo puedo ayudarte con información sobre PetCare. ¿Hay algo específico sobre nuestros productos o adopciones que te interese?"
3. NO uses información de internet para temas no relacionados con PetCare
4. NO respondas preguntas generales que no sean sobre la tienda

INFORMACIÓN ACTUAL DE PETCARE:

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
PetCare tiene un sistema completo de accesibilidad implementado. Las características disponibles son:

1. MODOS DE VISUALIZACIÓN (disponibles en la página de Accesibilidad):
   - Modo Estándar: Visualización por defecto con colores y contrastes estándar
   - Alto Contraste: Aumenta el contraste entre texto y fondo para mejorar la legibilidad. Ideal para personas con baja visión
   - Modo Daltónicos: Ajusta los colores para mejorar la distinción. Optimizado para protanopia y deuteranopia. ESTE MODO SÍ ESTÁ DISPONIBLE en PetCare

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

IMPORTANTE: Si un usuario pregunta sobre el "Modo Daltónicos" o "Modo para daltónicos", debes informar que SÍ está disponible en PetCare. Puede activarse desde la página de Accesibilidad (/accesibilidad/). El modo ajusta los colores para mejorar la distinción, especialmente para protanopia y deuteranopia.

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
        if settings.DEBUG:
            error_msg = f'Error inesperado: {str(e)}'
        else:
            error_msg = 'Ocurrió un error inesperado. Por favor intenta más tarde.'
        
        return JsonResponse({
            'success': False,
            'response': error_msg
        })
```

### 13.5 Agregar URL del chatbot

**Modificar `djangocrud/urls.py` (o tu archivo principal de URLs):**
```python
from core.views import chatbot

urlpatterns = [
    # ... URLs existentes ...
    path("chatbot/", chatbot, name="chatbot"),
]
```

**Nota:** Si usas i18n_patterns, agrega dentro de ellos:
```python
from django.conf.urls.i18n import i18n_patterns

urlpatterns_trans = i18n_patterns(
    # ... otras URLs ...
    path("chatbot/", chatbot, name="chatbot"),
)
```

### 13.6 Agregar widget del chatbot en `base.html`

**Al final del `<body>`, antes de `</body>`, agregar:**

```html
{# Chatbot Widget #}
{% if OPENAI_ENABLED %}
<div id="chatbot-widget" class="chatbot-widget">
    <div id="chatbot-toggle" class="chatbot-toggle">
        <i class="bi bi-chat-dots"></i>
    </div>
    <div id="chatbot-container" class="chatbot-container d-none">
        <div class="chatbot-header">
            <h6 class="mb-0">
                <i class="bi bi-robot me-2"></i>Asistente Virtual
            </h6>
            <button id="chatbot-close" class="btn btn-sm btn-link text-white p-0">
                <i class="bi bi-x-lg"></i>
            </button>
        </div>
        <div id="chatbot-messages" class="chatbot-messages">
            <div class="chatbot-message bot-message">
                <div class="message-content">
                    👋 ¡Hola! Soy tu asistente virtual de PetCare. ¿En qué puedo ayudarte hoy?
                    <br><small class="text-muted">Puedo ayudarte con información sobre productos, adopciones y más.</small>
                </div>
            </div>
        </div>
        <div class="chatbot-input-container">
            <input type="text" id="chatbot-input" class="form-control" placeholder="Escribe tu pregunta..." autocomplete="off">
            <button id="chatbot-send" class="btn btn-primary">
                <i class="bi bi-send"></i>
            </button>
        </div>
    </div>
</div>
<style>
    .chatbot-widget {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }
    .chatbot-toggle {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: transform 0.2s;
    }
    .chatbot-toggle:hover {
        transform: scale(1.1);
    }
    .chatbot-container {
        position: absolute;
        bottom: 80px;
        right: 0;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
    }
    .chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 12px 12px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chatbot-messages {
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        background: #f8f9fa;
    }
    .chatbot-message {
        margin-bottom: 15px;
        display: flex;
    }
    .bot-message {
        justify-content: flex-start;
    }
    .user-message {
        justify-content: flex-end;
    }
    .message-content {
        max-width: 80%;
        padding: 10px 15px;
        border-radius: 12px;
        word-wrap: break-word;
    }
    .bot-message .message-content {
        background: white;
        border: 1px solid #e0e0e0;
    }
    .user-message .message-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .chatbot-input-container {
        padding: 15px;
        border-top: 1px solid #e0e0e0;
        display: flex;
        gap: 10px;
    }
    #chatbot-input {
        flex: 1;
    }
    .chatbot-loading {
        display: inline-block;
        padding: 5px 10px;
    }
    .chatbot-loading::after {
        content: '...';
        animation: dots 1.5s steps(4, end) infinite;
    }
    @keyframes dots {
        0%, 20% { content: '.'; }
        40% { content: '..'; }
        60%, 100% { content: '...'; }
    }
</style>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const toggle = document.getElementById('chatbot-toggle');
        const container = document.getElementById('chatbot-container');
        const closeBtn = document.getElementById('chatbot-close');
        const sendBtn = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');
        const messages = document.getElementById('chatbot-messages');
        
        if (!toggle || !container) return;
        
        toggle.addEventListener('click', function() {
            container.classList.toggle('d-none');
        });
        
        closeBtn.addEventListener('click', function() {
            container.classList.add('d-none');
        });
        
        // Función para obtener CSRF token
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
        
        function addMessage(text, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'chatbot-message ' + (isUser ? 'user-message' : 'bot-message');
            messageDiv.innerHTML = '<div class="message-content">' + text + '</div>';
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
        
        function sendMessage() {
            const message = input.value.trim();
            if (!message) return;
            
            addMessage(message, true);
            input.value = '';
            
            // Mostrar loading
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'chatbot-message bot-message';
            loadingDiv.innerHTML = '<div class="message-content chatbot-loading">Pensando</div>';
            messages.appendChild(loadingDiv);
            messages.scrollTop = messages.scrollHeight;
            
            // Enviar a Django - Asegurar URL absoluta
            let chatbotUrl = '{% url "chatbot" %}';
            // Asegurar que empiece con /
            if (chatbotUrl && !chatbotUrl.startsWith('/')) {
                chatbotUrl = '/' + chatbotUrl;
            }
            
            fetch(chatbotUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') || ''
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error('Error del servidor: ' + text);
                    });
                }
                return response.json();
            })
            .then(data => {
                loadingDiv.remove();
                if (data.success) {
                    addMessage(data.response, false);
                } else {
                    addMessage(data.response || 'Lo siento, ocurrió un error. Por favor intenta nuevamente.', false);
                }
            })
            .catch(error => {
                loadingDiv.remove();
                addMessage('Error: ' + error.message, false);
                console.error('Chatbot error:', error);
            });
        }
        
        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    });
</script>
{% endif %}
```

### 13.7 Verificar funcionamiento

1. ✅ Verificar que `PERPLEXITY_API_KEY` esté configurada en `settings.py`
2. ✅ Verificar que el context processor esté agregado
3. ✅ Verificar que la URL del chatbot esté configurada
4. ✅ Verificar que el widget aparezca en la página (botón flotante)
5. ✅ Probar enviar un mensaje al chatbot
6. ✅ Verificar que las respuestas sean contextualizadas sobre PetCare

### 13.8 Solución de problemas comunes

**Error: "El chatbot no está configurado"**
- Verifica que `PERPLEXITY_API_KEY` tenga un valor en `settings.py`
- Verifica que `PERPLEXITY_ENABLED = True`

**Error: "Error de autenticación"**
- Verifica que la API key sea correcta
- Obtén una nueva API key en https://www.perplexity.ai/settings/api

**Error: "Cuota excedida"**
- Verifica tu plan de Perplexity
- Espera unos minutos o actualiza tu plan

**Error: "Invalid model"**
- El código intenta automáticamente diferentes modelos
- Si todos fallan, verifica tu plan de Perplexity

**El widget no aparece**
- Verifica que `OPENAI_ENABLED` esté en el contexto (context processor)
- Verifica que el template `base.html` tenga el código del widget
- Verifica la consola del navegador por errores JavaScript

---

## ⚠️ **ORDEN CRÍTICO ACTUALIZADO**

**NO cambies el orden, o tendrás errores:**

1. **Primero**: Modelos (Paso 2)
2. **Segundo**: Migraciones (Paso 2.4)
3. **Tercero**: Utilidades (Paso 3)
4. **Cuarto**: Formularios (Paso 4)
5. **Quinto**: Vistas (Paso 5)
6. **Sexto**: URLs (Paso 6)
7. **Séptimo**: Settings (Paso 7)
8. **Octavo**: Templates (Paso 8)
9. **Noveno**: Estáticos (Paso 9)
10. **Décimo**: Admin (Paso 10)
11. **Onceavo**: Migraciones finales (Paso 11)
12. **Doceavo**: Verificación (Paso 12)
13. **Treceavo**: Chatbot (Paso 13) ⭐ **NUEVO**

---

¡Buena suerte con la migración! 🚀

