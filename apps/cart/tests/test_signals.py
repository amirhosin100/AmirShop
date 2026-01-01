from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.market.models import Market
from apps.cart.models import Cart, CartItem
from apps.product.models import Product
from apps.user.models import Marketer

User = get_user_model()


class CartSignalTest(TestCase):
    """Tests for post_save signal on CartItem that updates Cart.amount."""

    @classmethod
    def setUpTestData(cls):
        # Create user and market
        cls.user = User.objects.create_user(phone="09123456789", password="testpass123")
        Marketer.objects.create(user=cls.user)
        cls.market = Market.objects.create(marketer=cls.user.marketer, name="Test Market")

        # Create products
        cls.product1 = Product.objects.create(
            market=cls.market,
            name="Product 1",
            price=100_000,
            percentage_off=20,  # discount_price = 80_000
            stock=100,
        )
        cls.product2 = Product.objects.create(
            market=cls.market,
            name="Product 2",
            price=200_000,
            percentage_off=0,  # discount_price = 200_000
            stock=50,
        )

    def setUp(self):
        self.cart = Cart.manage_items.get_cart(self.user)

    def test_signal_updates_amount_on_create_cart_item(self):
        """Creating a CartItem should update Cart.amount."""
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 2 * 80_000)  # 160_000

    def test_signal_updates_amount_on_update_cart_item(self):
        """Updating CartItem quantity should update Cart.amount."""
        item = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=1)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 80_000)

        item.quantity = 3
        item.save()
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 3 * 80_000)  # 240_000

    def test_signal_updates_amount_on_multiple_items(self):
        """Multiple CartItems should sum final_prices correctly."""
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)  # 160_000
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)  # 200_000
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 160_000 + 200_000)  # 360_000

        # Update one item
        item2 = self.cart.items.get(product=self.product2)
        item2.quantity = 2
        item2.save()
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 160_000 + 400_000)  # 560_000

    def test_signal_updates_amount_on_delete_cart_item(self):
        """Deleting a CartItem should update Cart.amount (via manager or manual)."""
        item1 = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)  # 160_000
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)  # 200_000
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 360_000)

        item1.delete()
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 200_000)  # Only item2 remains

    def test_signal_handles_empty_cart_amount_zero(self):
        """Empty cart should have amount=0."""
        self.assertEqual(self.cart.amount, 0)

        # Add and delete
        item = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=1)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 80_000)

        item.delete()
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 0)

    def test_signal_updates_on_product_discount_change(self):
        """If product discount changes, saving CartItem updates final_price and amount."""
        item = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 160_000)

        # Change product discount
        self.product1.percentage_off = 50  # discount_price = 50_000
        self.product1.save()

        # Re-save item to trigger final_price update and signal
        item.save()
        self.cart.refresh_from_db()
        self.assertEqual(item.final_price, 2 * 50_000)
        self.assertEqual(self.cart.amount, 100_000)

    def test_signal_not_triggered_on_other_saves(self):
        """Signal should only trigger on CartItem save, not Cart."""
        self.cart.amount = 999  # Manual change
        self.cart.save()
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 999)  # No items, but manual save doesn't trigger item signal

        # Now add item
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=1)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.amount, 80_000)  # Overwrites to correct sum