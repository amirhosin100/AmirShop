# apps/cart/tests/test_serializers.py
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.market.models import Market
from apps.product.models import Product
from apps.cart.models import Cart, CartItem
from apps.cart.serializer.user_serializer import CartItemSerializer, CartSerializer
from apps.user.models import Marketer

User = get_user_model()


class CartItemSerializerTest(TestCase):
    """Tests for CartItemSerializer"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(phone="09123456789", password="testpass123")
        Marketer.objects.create(user=cls.user)
        cls.market = Market.objects.create(marketer=cls.user.marketer, name="Test Market")

        cls.product = Product.objects.create(
            market=cls.market,
            name="Fantastic Product",
            price=150_000,
            percentage_off=10,  # discount_price = 135_000
            stock=100,
        )

    def setUp(self):
        self.cart = Cart.manage_items.get_cart(self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )
        self.cart_item.refresh_from_db()  # final_price = 405_000

    def test_serializer_fields(self):
        serializer = CartItemSerializer(instance=self.cart_item)
        data = serializer.data
        expected_fields = {'id', 'product', 'product_name', 'quantity', 'final_price'}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_product_name_custom_field(self):
        serializer = CartItemSerializer(instance=self.cart_item)
        self.assertEqual(serializer.data['product_name'], "Fantastic Product")

    def test_final_price_correct_calculation(self):
        serializer = CartItemSerializer(instance=self.cart_item)
        self.assertEqual(serializer.data['final_price'], 405_000)

    def test_read_only_fields_ignored_on_update(self):
        """Only quantity should be updatable; others are read-only"""
        data = {
            'product': 999,
            'product_name': "Hacked Name",
            'final_price': 999999,
            'id': 999,
            'quantity': 8
        }
        serializer = CartItemSerializer(instance=self.cart_item, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 8)
        self.assertEqual(self.cart_item.final_price, 8 * 135_000)
        self.assertEqual(self.cart_item.product.id, self.product.id)  # unchanged

    def test_quantity_validation_rejects_non_positive(self):
        """quantity <= 0 should fail validation"""
        for qty in [0, -5]:
            serializer = CartItemSerializer(
                instance=self.cart_item,
                data={'quantity': qty},
                partial=True
            )
            self.assertFalse(serializer.is_valid())
            self.assertIn('quantity', serializer.errors)

    def test_valid_quantity_updates_final_price(self):
        serializer = CartItemSerializer(
            instance=self.cart_item,
            data={'quantity': 5},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 5)
        self.assertEqual(self.cart_item.final_price, 5 * 135_000)


class CartSerializerTest(TestCase):
    """Tests for CartSerializer with nested read-only items"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(phone="09121234567", password="testpass")
        Marketer.objects.create(user=cls.user)
        cls.market = Market.objects.create(marketer=cls.user.marketer, name="Another Market")

        cls.product1 = Product.objects.create(
            market=cls.market,
            name="Product A",
            price=100_000,
            percentage_off=0,
            stock=50,
        )
        cls.product2 = Product.objects.create(
            market=cls.market,
            name="Product B",
            price=200_000,
            percentage_off=50,  # discount_price = 100_000
            stock=30,
        )

    def setUp(self):
        self.cart = Cart.manage_items.get_cart(self.user)
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)  # 200_000
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)  # 100_000

    def test_cart_serializer_nested_items_output(self):
        serializer = CartSerializer(instance=self.cart)
        data = serializer.data

        self.assertEqual(len(data['items']), 2)
        names = {item['product_name'] for item in data['items']}
        self.assertEqual(names, {"Product A", "Product B"})

        item_a = next(i for i in data['items'] if i['product_name'] == "Product A")
        self.assertEqual(item_a['quantity'], 2)
        self.assertEqual(item_a['final_price'], 200_000)

    def test_cart_serializer_fields(self):
        serializer = CartSerializer(instance=self.cart)
        self.assertEqual(set(serializer.data.keys()), {'id', 'amount', 'items'})

    def test_read_only_nested_items_prevent_update_error(self):
        """Trying to send items in input should be ignored safely (no update error)"""
        data = {
            'amount': 999999,
            'items': [{'product': 999, 'quantity': 10}],
            'id': 999
        }
        serializer = CartSerializer(instance=self.cart, data=data, partial=True)

        # حالا باید بدون خطا valid باشه و save بشه
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(AssertionError):
            serializer.save()

        # هیچ تغییری در آیتم‌ها نباید اعمال شده باشه
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 2)

    def test_empty_cart_serialization(self):
        empty_user = User.objects.create_user(phone="09999999999", password="empty")
        empty_cart = Cart.manage_items.get_cart(empty_user)
        serializer = CartSerializer(instance=empty_cart)
        self.assertEqual(serializer.data['items'], [])
        self.assertEqual(serializer.data['amount'], 0)

    def test_cart_with_single_item(self):
        single_user = User.objects.create_user(phone="09888888888", password="single")
        cart = Cart.manage_items.get_cart(single_user)
        Cart.manage_items.add(single_user, self.product1)

        serializer = CartSerializer(instance=cart)
        self.assertEqual(len(serializer.data['items']), 1)
        self.assertEqual(serializer.data['items'][0]['quantity'], 1)
        self.assertEqual(serializer.data['items'][0]['product_name'], "Product A")