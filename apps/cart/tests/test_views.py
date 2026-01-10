from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
import uuid

from apps.market.models import Market
from apps.product.models import Product
from apps.cart.models import Cart, CartItem, CartInfo
from apps.user.models import Marketer

User = get_user_model()


class CartViewsTestCase(APITestCase):
    """Comprehensive tests for all cart-related API views, covering all scenarios."""

    @classmethod
    def setUpTestData(cls):
        # Create test users and marketers
        cls.user = User.objects.create_user(phone="09123456789", password="testpass123")
        Marketer.objects.create(
            user=cls.user,
            age=20,
            national_code="1234567890",
            city="city",
            province="province",
            address="address",
        )

        cls.user2 = User.objects.create_user(phone="09876543210", password="anotherpass")
        Marketer.objects.create(
            user=cls.user2,
            age=20,
            national_code="1234567890",
            city="city",
            province="province",
            address="address",
        )

        # Create market and products
        cls.market = Market.objects.create(marketer=cls.user.marketer, name="Test Market")
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

        # URLs for views
        cls.cart_detail_url = reverse('cart_user:cart_detail')
        cls.add_to_cart_url = lambda pid: reverse('cart_user:add_to_cart', kwargs={'product_id': pid})
        cls.decrease_item_url = lambda pid: reverse('cart_user:decrease_item', kwargs={'product_id': pid})
        cls.set_quantity_url = lambda pid: reverse('cart_user:set_item_quantity', kwargs={'product_id': pid})
        cls.remove_item_url = lambda pid: reverse('cart_user:remove_cart', kwargs={'product_id': pid})
        cls.clear_cart_url = reverse('cart_user:cart_clear')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.cart = Cart.manage_items.get_cart(self.user)

    # CartDetailView Tests
    def test_cart_detail_view_get_success_with_items(self):
        """GET cart detail should return cart with items."""
        Cart.manage_items.add(self.user, self.product1)
        Cart.manage_items.add(self.user, self.product2)

        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertEqual(len(response.data['items']), 2)
        self.assertEqual(response.data['amount'], 280000)  # Adjust if amount auto-updates

    def test_cart_detail_view_get_success_empty_cart(self):
        """GET cart detail for empty cart should return empty items."""
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertEqual(len(response.data['items']), 0)
        self.assertEqual(response.data['amount'], 0)

    def test_cart_detail_view_unauthenticated_fails(self):
        """Unauthenticated GET should return 403."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # AddToCartView Tests
    def test_add_to_cart_success_adds_one(self):
        """POST always adds 1, ignoring any quantity."""
        response = self.client.post(self.add_to_cart_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 1)
        self.assertEqual(response.data['final_price'], 80_000)

        item = CartItem.objects.get(cart=self.cart, product=self.product1)
        self.assertEqual(item.quantity, 1)

    def test_add_to_cart_with_quantity_ignored_adds_one(self):
        """POST with quantity (int or str) ignored, adds 1."""
        data = {'quantity': 5}
        response = self.client.post(self.add_to_cart_url(self.product1.id), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 1)  # Ignored, adds 1

        data = {'quantity': '3'}
        response = self.client.post(self.add_to_cart_url(self.product2.id), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 1)  # Ignored

    def test_add_to_cart_existing_item_increments_by_one(self):
        """Adding existing item increments by 1."""
        Cart.manage_items.set(self.user, self.product1, quantity=2)
        response = self.client.post(self.add_to_cart_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 3)

    def test_add_to_cart_nonexistent_product_fails(self):
        """POST with invalid product_id should return 404."""
        response = self.client.post(self.add_to_cart_url(uuid.uuid4()))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Product does not exist', response.data['message'])

    def test_add_to_cart_unauthenticated_fails(self):
        """Unauthenticated POST should return 403."""
        self.client.force_authenticate(user=None)
        response = self.client.post(self.add_to_cart_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # DecreaseCartItemView Tests
    def test_decrease_cart_item_success(self):
        """POST decrease should reduce quantity if >1, else stay 1."""
        Cart.manage_items.set(self.user, self.product1, quantity=3)
        response = self.client.post(self.decrease_item_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 2)

    def test_decrease_cart_item_quantity_one_stays_one(self):
        """Decrease on quantity=1 stays 1."""
        Cart.manage_items.add(self.user, self.product1)
        response = self.client.post(self.decrease_item_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 1)

    def test_decrease_cart_item_not_in_cart_fails(self):
        """POST decrease on missing item fails."""
        response = self.client.post(self.decrease_item_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This product don't exist in your cart", response.data['message'])

    def test_decrease_nonexistent_product_fails(self):
        """POST decrease with invalid product_id 404."""
        response = self.client.post(self.decrease_item_url(uuid.uuid4()))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decrease_cart_item_unauthenticated_fails(self):
        """Unauthenticated decrease 403."""
        self.client.force_authenticate(user=None)
        response = self.client.post(self.decrease_item_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # SetItemQuantityView Tests
    def test_set_item_quantity_success(self):
        """POST set quantity updates or creates if quantity provided."""
        data = {'quantity': 4}
        response = self.client.post(self.set_quantity_url(self.product1.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 4)

    def test_set_item_quantity_on_existing_updates(self):
        """Set on existing updates quantity."""
        Cart.manage_items.add(self.user, self.product1)
        data = {'quantity': 6}
        response = self.client.post(self.set_quantity_url(self.product1.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 6)

    def test_set_item_quantity_no_quantity_fails_custom_error(self):
        """POST without quantity fails with custom error."""
        response = self.client.post(self.set_quantity_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity is required', response.data['error'])

    def test_set_item_quantity_non_int_fails(self):
        """POST with non-int quantity fails serializer."""
        data = {'quantity': 'abc'}
        response = self.client.post(self.set_quantity_url(self.product1.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('A valid integer is required', str(response.data['quantity']))

    def test_set_item_quantity_zero_fails(self):
        """POST with quantity=0 fails serializer."""
        data = {'quantity': 0}
        response = self.client.post(self.set_quantity_url(self.product1.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Quantity must be positive', str(response.data['quantity']))

    def test_set_item_quantity_negative_fails(self):
        """POST with negative quantity fails serializer."""
        data = {'quantity': -1}
        response = self.client.post(self.set_quantity_url(self.product1.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Ensure this value is greater than or equal to 0.', str(response.data['quantity']))

    def test_set_item_quantity_nonexistent_product_fails(self):
        """POST set with invalid product 404."""
        data = {'quantity': 5}
        response = self.client.post(self.set_quantity_url(uuid.uuid4()), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_set_item_quantity_unauthenticated_fails(self):
        """Unauthenticated set 403."""
        self.client.force_authenticate(user=None)
        data = {'quantity': 5}
        response = self.client.post(self.set_quantity_url(self.product1.id), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # RemoveCartItemView Tests
    def test_remove_cart_item_success(self):
        """DELETE removes item."""
        Cart.manage_items.add(self.user, self.product1)
        response = self.client.delete(self.remove_item_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('product has been removed', response.data['message'])
        self.assertFalse(CartItem.objects.filter(product=self.product1).exists())

    def test_remove_cart_item_not_in_cart_fails(self):
        """DELETE on missing item fails."""
        response = self.client.delete(self.remove_item_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("product doesn't exist to cart", response.data['message'])

    def test_remove_nonexistent_product_fails(self):
        """DELETE with invalid product 404."""
        response = self.client.delete(self.remove_item_url(uuid.uuid4()))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_cart_item_unauthenticated_fails(self):
        """Unauthenticated remove 403."""
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.remove_item_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # CartClearView Tests
    def test_clear_cart_success_with_items(self):
        """POST clear removes all items."""
        Cart.manage_items.add(self.user, self.product1)
        Cart.manage_items.add(self.user, self.product2)
        response = self.client.post(self.clear_cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 0)
        self.assertEqual(self.cart.items.count(), 0)

    def test_clear_empty_cart_success(self):
        """POST clear on empty cart succeeds."""
        response = self.client.post(self.clear_cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 0)

    def test_clear_cart_unauthenticated_fails(self):
        """Unauthenticated clear 403."""
        self.client.force_authenticate(user=None)
        response = self.client.post(self.clear_cart_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Additional Cross-View and Multi-User Tests
    def test_multi_user_carts_independent(self):
        """Operations on one user's cart don't affect another's."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.add_to_cart_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(len(response.data['items']), 0)

    def test_add_and_then_decrease(self):
        """Add and then decrease works correctly."""
        self.client.post(self.add_to_cart_url(self.product1.id))
        response = self.client.post(self.decrease_item_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 1)  # Stays 1

    def test_set_and_then_remove(self):
        """Set quantity and then remove item."""
        self.client.post(self.set_quantity_url(self.product1.id), {'quantity': 2})
        response = self.client.delete(self.remove_item_url(self.product1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CartItem.objects.filter(product=self.product1).exists())

    def test_clear_and_then_add(self):
        """Clear cart and then add new item."""
        Cart.manage_items.add(self.user, self.product1)
        self.client.post(self.clear_cart_url)
        response = self.client.post(self.add_to_cart_url(self.product2.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.filter(cart=self.cart).count(), 1)
        self.assertEqual(CartItem.objects.get(cart=self.cart).product, self.product2)


class CartInfoTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.main_user = User.objects.create(
            phone='09123456789',
        )
        cls.other_user = User.objects.create(
            phone='09123456799',
        )
        cls.cart_info = CartInfo.objects.create(
            user=cls.main_user,
            amount=100
        )
        cls.detail_url = lambda pk: reverse('cart_user:cart_info_detail', kwargs={'pk': pk})
        cls.list_url = reverse('cart_user:cart_info_list')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.main_user)

    def test_detail_by_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(
            self.detail_url(self.cart_info.id)
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(
            self.detail_url(self.cart_info.id)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_by_owner_user(self):
        response = self.client.get(
            self.detail_url(self.cart_info.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], 100)

    def test_list_by_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_by_authenticate_user(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
