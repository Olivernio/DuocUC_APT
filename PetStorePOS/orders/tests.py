"""
Tests básicos para el módulo de órdenes.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Order, OrderItem, OrderStatus, Coupon, DiscountType
from catalog.models import Product, Category


class OrderModelTest(TestCase):
    """Tests para el modelo Order"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            sku='TST',
            name='Producto Test',
            category=Category.FOOD,
            price=10000,
            stock=10
        )
    
    def test_order_creation(self):
        """Test: Crear una orden básica"""
        order = Order.objects.create(
            user=self.user,
            status=OrderStatus.PENDING,
            total=10000,
            shipping_address='Calle Test 123',
            shipping_city='Santiago'
        )
        
        self.assertIsNotNone(order.order_number)
        self.assertTrue(order.order_number.startswith('ORD-'))
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(order.user, self.user)
    
    def test_order_number_uniqueness(self):
        """Test: Los números de orden son únicos"""
        order1 = Order.objects.create(
            user=self.user,
            status=OrderStatus.PENDING,
            total=10000
        )
        order2 = Order.objects.create(
            user=self.user,
            status=OrderStatus.PENDING,
            total=20000
        )
        
        self.assertNotEqual(order1.order_number, order2.order_number)
    
    def test_order_with_items(self):
        """Test: Crear orden con items"""
        order = Order.objects.create(
            user=self.user,
            status=OrderStatus.PENDING,
            total=20000
        )
        
        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=10000
        )
        
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(item.subtotal, 20000)


class CouponModelTest(TestCase):
    """Tests para el modelo Coupon"""
    
    def setUp(self):
        """Configuración inicial"""
        from django.utils import timezone
        from datetime import timedelta
        
        self.now = timezone.now()
        self.valid_from = self.now - timedelta(days=1)
        self.valid_to = self.now + timedelta(days=30)
    
    def test_coupon_creation(self):
        """Test: Crear un cupón"""
        coupon = Coupon.objects.create(
            code='TEST20',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=20,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            is_active=True
        )
        
        self.assertEqual(coupon.code, 'TEST20')
        self.assertTrue(coupon.is_valid())
    
    def test_coupon_calculate_discount_percentage(self):
        """Test: Calcular descuento porcentual"""
        coupon = Coupon.objects.create(
            code='TEST20',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=20,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            is_active=True
        )
        
        discount, final = coupon.calculate_discount(10000)
        self.assertEqual(discount, 2000)
        self.assertEqual(final, 8000)
    
    def test_coupon_calculate_discount_fixed(self):
        """Test: Calcular descuento fijo"""
        coupon = Coupon.objects.create(
            code='TEST1000',
            discount_type=DiscountType.FIXED,
            discount_value=1000,
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            is_active=True
        )
        
        discount, final = coupon.calculate_discount(5000)
        self.assertEqual(discount, 1000)
        self.assertEqual(final, 4000)
    
    def test_coupon_expired(self):
        """Test: Cupón expirado no es válido"""
        from datetime import timedelta
        
        expired_coupon = Coupon.objects.create(
            code='EXPIRED',
            discount_type=DiscountType.PERCENTAGE,
            discount_value=10,
            valid_from=self.now - timedelta(days=60),
            valid_to=self.now - timedelta(days=30),
            is_active=True
        )
        
        self.assertFalse(expired_coupon.is_valid())
