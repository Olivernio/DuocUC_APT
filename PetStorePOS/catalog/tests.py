"""
Tests básicos para el módulo de catálogo.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Product, Category, ProductReview


class ProductModelTest(TestCase):
    """Tests para el modelo Product"""
    
    def setUp(self):
        """Configuración inicial"""
        self.product = Product.objects.create(
            sku='TST',
            name='Producto Test',
            category=Category.FOOD,
            price=10000,
            stock=10,
            description='Descripción de prueba'
        )
    
    def test_product_creation(self):
        """Test: Crear un producto"""
        self.assertEqual(self.product.sku, 'TST')
        self.assertEqual(self.product.name, 'Producto Test')
        self.assertEqual(self.product.category, Category.FOOD)
        self.assertEqual(self.product.price, 10000)
        self.assertEqual(self.product.stock, 10)
    
    def test_product_str(self):
        """Test: Representación string del producto"""
        self.assertEqual(str(self.product), 'TST · Producto Test')
    
    def test_product_get_average_rating(self):
        """Test: Calcular promedio de rating"""
        user = User.objects.create_user(username='testuser', password='test123')
        
        # Crear reseñas
        ProductReview.objects.create(
            product=self.product,
            user=user,
            rating=5,
            is_approved=True
        )
        ProductReview.objects.create(
            product=self.product,
            user=User.objects.create_user(username='testuser2', password='test123'),
            rating=3,
            is_approved=True
        )
        
        avg_rating = self.product.get_average_rating()
        self.assertEqual(avg_rating, 4.0)
    
    def test_product_get_total_reviews(self):
        """Test: Contar reseñas aprobadas"""
        user = User.objects.create_user(username='testuser', password='test123')
        
        ProductReview.objects.create(
            product=self.product,
            user=user,
            rating=5,
            is_approved=True
        )
        ProductReview.objects.create(
            product=self.product,
            user=User.objects.create_user(username='testuser2', password='test123'),
            rating=3,
            is_approved=False  # No aprobada
        )
        
        total = self.product.get_total_reviews()
        self.assertEqual(total, 1)


class ProductReviewModelTest(TestCase):
    """Tests para el modelo ProductReview"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test123'
        )
        self.product = Product.objects.create(
            sku='TST',
            name='Producto Test',
            category=Category.FOOD,
            price=10000,
            stock=10
        )
    
    def test_review_creation(self):
        """Test: Crear una reseña"""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Excelente producto',
            is_approved=False
        )
        
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)
        self.assertFalse(review.is_approved)
    
    def test_review_unique_together(self):
        """Test: Un usuario solo puede dejar una reseña por producto"""
        ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5
        )
        
        # Intentar crear otra reseña del mismo usuario para el mismo producto
        # Debe fallar por unique_together
        with self.assertRaises(Exception):
            ProductReview.objects.create(
                product=self.product,
                user=self.user,
                rating=3
            )
