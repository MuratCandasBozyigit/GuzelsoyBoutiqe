from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import (
    Category,
    Product,
    ProductImage,
    SizeVariant,
    Cart,
    CartItem,
    Order,
    OrderItem,
    PaymentLog
)

User = get_user_model()


class GalaButikModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Büyük Beden Elbise",
            slug="buyuk-beden-elbise",
            description="Özel dökümlü elbiseler"
        )
        self.product = Product.objects.create(
            category=self.category,
            name="Viskon Büyük Beden Çiçekli Elbise",
            sku="GLA-TEST-01",
            price=Decimal("1000.00"),
            discount_price=Decimal("800.00"),
            description="Test açıklama",
            fabric_info="%100 Viskon"
        )
        self.variant_xl = SizeVariant.objects.create(
            product=self.product,
            size="XL (42-44)",
            stock=10
        )
        self.variant_2xl = SizeVariant.objects.create(
            product=self.product,
            size="2XL (46-48)",
            stock=5
        )

    def test_product_discount_and_installment(self):
        self.assertTrue(self.product.has_discount)
        self.assertEqual(self.product.current_price, Decimal("800.00"))
        self.assertEqual(self.product.discount_percent, 20)
        self.assertEqual(self.product.total_stock, 15)
        self.assertTrue(self.product.is_in_stock)
        # 3 Installments rule check
        self.assertEqual(self.product.installment_3x, Decimal("266.67"))

    def test_cart_calculations_and_shipping(self):
        cart = Cart.objects.create(session_key="test_session_123")
        item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            size_variant=self.variant_xl,
            quantity=1
        )
        # Subtotal is 800.00 TL (>= 750 TL threshold for free shipping)
        self.assertEqual(cart.subtotal, Decimal("800.00"))
        self.assertEqual(cart.shipping_fee, Decimal("0.00"))
        self.assertEqual(cart.total_amount, Decimal("800.00"))
        self.assertEqual(cart.remaining_for_free_shipping, Decimal("0.00"))

    def test_payment_log_max_3_installments_rule(self):
        order = Order.objects.create(
            first_name="Fatma",
            last_name="Yılmaz",
            email="fatma@example.com",
            phone="05330001122",
            address_line1="Test Cad. No:5",
            district="Beşiktaş",
            city="İstanbul",
            subtotal=Decimal("800.00"),
            shipping_fee=Decimal("0.00"),
            total_amount=Decimal("800.00"),
            installments=3
        )
        
        # Valid 3 installments log
        valid_log = PaymentLog(
            order=order,
            provider="paytr",
            status="success",
            installment_count=3,
            amount=Decimal("800.00")
        )
        valid_log.full_clean()  # should not raise
        valid_log.save()
        self.assertEqual(valid_log.installment_count, 3)

        # Invalid >3 installments log (must fail validation)
        invalid_log = PaymentLog(
            order=order,
            provider="paytr",
            status="pending",
            installment_count=6,
            amount=Decimal("800.00")
        )
        with self.assertRaises(ValidationError):
            invalid_log.full_clean()


class GalaButikViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name="İkili Takım",
            slug="ikili-takim"
        )
        self.product = Product.objects.create(
            category=self.category,
            name="Triko İkili Takım",
            sku="GLA-TKM-01",
            price=Decimal("1200.00"),
            description="Rahat kalıp takım"
        )
        self.variant = SizeVariant.objects.create(
            product=self.product,
            size="XL (42-44)",
            stock=8
        )

    def test_home_page_status(self):
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gala")

    def test_product_list_status(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Triko İkili Takım")

    def test_product_detail_status(self):
        response = self.client.get(reverse('store:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Triko İkili Takım")
        self.assertContains(response, "Taksit Seçenekleri")

    def test_add_to_cart_and_checkout_flow(self):
        # 1. Add to cart
        add_res = self.client.post(reverse('store:add_to_cart'), {
            'product_id': self.product.id,
            'size_variant_id': self.variant.id,
            'quantity': 1
        })
        self.assertEqual(add_res.status_code, 302)

        # 2. View cart
        cart_res = self.client.get(reverse('store:cart_detail'))
        self.assertEqual(cart_res.status_code, 200)
        self.assertContains(cart_res, "Triko İkili Takım")

        # 3. Checkout POST
        checkout_res = self.client.post(reverse('store:checkout'), {
            'first_name': 'Zeynep',
            'last_name': 'Kaya',
            'email': 'zeynep@example.com',
            'phone': '05551234567',
            'city': 'İzmir',
            'district': 'Konak',
            'address_line1': 'Güzelyalı Mah. 42. Sok No:10',
            'payment_method': 'credit_card',
            'installments': '3'
        })
        self.assertEqual(checkout_res.status_code, 302)
        
        # Verify order created
        order = Order.objects.get(email='zeynep@example.com')
        self.assertEqual(order.installments, 3)
        self.assertEqual(order.status, 'confirmed')
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.payment_logs.count(), 1)
        self.assertEqual(order.payment_logs.first().installment_count, 3)
