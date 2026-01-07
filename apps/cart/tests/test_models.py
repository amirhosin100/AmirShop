from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from apps.market.models import Market
from apps.product.models import Product
from apps.cart.models import Cart, CartItem
from apps.user.models import Marketer

User = get_user_model()


class CartAndCartItemTest(TestCase):
    """
    Comprehensive tests for Cart and CartItem models along with CartManager methods.
    """

    @classmethod
    def setUpTestData(cls):
        """Create shared test data: user, marketer, and market."""
        cls.user = User.objects.create_user(phone="09123456789", password="testpass123")
        Marketer.objects.create(
            user=cls.user,
            age=20,
            national_code="1234567890",
            city="city",
            province="province",
            address="address",
        )

        cls.market = Market.objects.create(
            marketer=cls.user.marketer,
            name="Test Market"
        )

    def setUp(self):
        """Create products for each test method."""
        self.product1 = Product.objects.create(
            market=self.market,
            name="First Product",
            price=100_000,
            percentage_off=20,  # discount_price = 80_000
            stock=100,
        )
        self.product2 = Product.objects.create(
            market=self.market,
            name="Second Product",
            price=200_000,
            percentage_off=0,   # discount_price = 200_000
            stock=50,
        )

    def test_get_cart_creates_and_reuses_cart(self):
        """get_cart should create a cart on first call and reuse it on subsequent calls."""
        cart1 = Cart.manage_items.get_cart(self.user)
        self.assertEqual(Cart.objects.count(), 1)
        self.assertEqual(cart1.user, self.user)

        cart2 = Cart.manage_items.get_cart(self.user)
        self.assertEqual(cart1, cart2)
        self.assertEqual(Cart.objects.count(), 1)

    def test_add_product_increases_quantity(self):
        """add() should add a new item or increment quantity of an existing one."""
        item = Cart.manage_items.add(self.user, self.product1)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.final_price, 80_000)

        item2 = Cart.manage_items.add(self.user, self.product1)
        self.assertEqual(item2.quantity, 2)
        self.assertEqual(item2.final_price, 160_000)
        self.assertEqual(CartItem.objects.filter(cart__user=self.user).count(), 1)

    def test_set_quantity_directly(self):
        """set() should directly set the quantity of an item."""
        item = Cart.manage_items.set(self.user, self.product1, quantity=5)
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.final_price, 5 * 80_000)

        item = Cart.manage_items.set(self.user, self.product1, quantity=1)
        self.assertEqual(item.quantity, 1)

        with self.assertRaises(ValueError):
            Cart.manage_items.set(self.user, self.product1, quantity=0)
        with self.assertRaises(ValueError):
            Cart.manage_items.set(self.user, self.product1, quantity=-5)

    def test_decrease_quantity(self):
        """decrease() should reduce quantity but never go below 1."""
        Cart.manage_items.add(self.user, self.product1)
        Cart.manage_items.add(self.user, self.product1)  # quantity = 2

        item = Cart.manage_items.decrease(self.user, self.product1)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.final_price, 80_000)

        item = Cart.manage_items.decrease(self.user, self.product1)
        self.assertEqual(item.quantity, 1)  # stays at 1

        with self.assertRaises(ValueError):
            Cart.manage_items.decrease(self.user, self.product2)

    def test_remove_product(self):
        """remove() should completely delete the cart item."""
        Cart.manage_items.add(self.user, self.product1)

        result = Cart.manage_items.remove(self.user, self.product1)
        self.assertTrue(result)

        self.assertFalse(
            CartItem.objects.filter(cart__user=self.user, product=self.product1).exists()
        )

        with self.assertRaises(ValueError):
            Cart.manage_items.remove(self.user, self.product1)

    def test_clear_cart(self):
        """clear() should remove all items while keeping the cart object."""
        Cart.manage_items.add(self.user, self.product1)
        Cart.manage_items.add(self.user, self.product2)
        Cart.manage_items.add(self.user, self.product1)

        cart = Cart.manage_items.clear(self.user)

        self.assertEqual(cart.items.count(), 0)
        self.assertEqual(CartItem.objects.filter(cart__user=self.user).count(), 0)
        self.assertTrue(Cart.objects.filter(user=self.user).exists())

    def test_cart_item_final_price_calculation_on_save(self):
        """final_price should always be quantity × product.discount_price on save."""
        cart = Cart.manage_items.get_cart(self.user)
        item = CartItem.objects.create(cart=cart, product=self.product1, quantity=3)
        self.assertEqual(item.final_price, 3 * 80_000)

        item.quantity = 10
        item.save()
        self.assertEqual(item.final_price, 10 * 80_000)

        # Change product discount and save item again
        self.product1.percentage_off = 50  # discount_price = 50_000
        self.product1.save()

        item.save()
        self.assertEqual(item.final_price, 10 * 50_000)

    def test_cart_item_default_quantity(self):
        """CartItem should have default quantity of 1."""
        cart = Cart.manage_items.get_cart(self.user)
        item = CartItem.objects.create(cart=cart, product=self.product1)

        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.final_price, 80_000)

    def test_unique_together_cart_and_product(self):
        """CartItem should enforce unique constraint on (cart, product)."""
        cart = Cart.manage_items.get_cart(self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=1)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CartItem.objects.create(cart=cart, product=self.product1, quantity=5)

    def test_cart_one_to_one_with_user(self):
        """Cart should have a OneToOne relationship with User."""
        cart = Cart.manage_items.get_cart(self.user)
        self.assertEqual(self.user.cart, cart)

        with self.assertRaises(IntegrityError):
            Cart.objects.create(user=self.user)

    def test_cart_str_representation(self):
        """__str__ of Cart should display user phone and amount."""
        cart = Cart.manage_items.get_cart(self.user)
        self.assertEqual(str(cart), f"{self.user.phone} : 0")

        Cart.manage_items.add(self.user, self.product1)
        cart.refresh_from_db()
        self.assertIn(self.user.phone, str(cart))

    def test_cart_item_str_representation(self):
        """__str__ of CartItem should show product name and final price."""
        item = Cart.manage_items.add(self.user, self.product1)
        self.assertEqual(str(item), f"{self.product1.name} : {item.final_price}")

    # ====================== NEW TESTS ======================

    def test_add_multiple_different_products(self):
        """Adding different products should create separate cart items."""
        Cart.manage_items.add(self.user, self.product1)
        Cart.manage_items.add(self.user, self.product2)

        self.assertEqual(CartItem.objects.filter(cart__user=self.user).count(), 2)
        self.assertEqual(self.user.cart.items.filter(product=self.product1).first().quantity, 1)
        self.assertEqual(self.user.cart.items.filter(product=self.product2).first().quantity, 1)

    def test_decrease_when_quantity_is_one_does_not_remove_item(self):
        """decrease() on quantity=1 should keep the item with quantity=1."""
        Cart.manage_items.add(self.user, self.product1)  # quantity = 1

        item = Cart.manage_items.decrease(self.user, self.product1)
        self.assertEqual(item.quantity, 1)
        self.assertTrue(CartItem.objects.filter(product=self.product1).exists())

    def test_set_quantity_to_zero_raises_error_but_does_not_remove(self):
        """set() with invalid quantity raises ValueError without affecting existing items."""
        Cart.manage_items.add(self.user, self.product1)

        with self.assertRaises(ValueError):
            Cart.manage_items.set(self.user, self.product1, quantity=0)

        # Item should still exist with original quantity
        self.assertTrue(CartItem.objects.filter(product=self.product1).exists())
        self.assertEqual(self.user.cart.items.get(product=self.product1).quantity, 1)

    def test_atomicity_of_manager_methods(self):
        """All manager methods are decorated with @transaction.atomic – test rollback on error."""
        Cart.manage_items.add(self.user, self.product1)

        # Simulate an error inside an atomic method (set with invalid quantity)
        with self.assertRaises(ValueError):
            Cart.manage_items.set(self.user, self.product1, quantity=-1)

        # Cart state should remain unchanged
        item = self.user.cart.items.get(product=self.product1)
        self.assertEqual(item.quantity, 1)