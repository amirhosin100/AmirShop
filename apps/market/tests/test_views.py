from rest_framework import test, status, permissions
from unittest.mock import patch
from uuid import uuid4
from apps.market.models import Market
from django.urls import reverse
from apps.user.models import User, Marketer
from permissions.market import IsMarketer, IsMarketOwner
from apps.market.views.owner_views import (
    MarketOwnerListView,
    MarketOwnerCreateView,
    MarketOwnerDeleteView,
    MarketOwnerDetailView,
    MarketOwnerUpdateView
)
from apps.market.views.user_views import (
    AllMarketsView,
    MarketDetailView
)


class BaseMarketOwnerTest(test.APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = test.APIRequestFactory()
        cls.client = test.APIClient()

        cls.owner_user = User.objects.create(
            phone='09123456789'
        )

        Marketer.objects.create(
            user=cls.owner_user,
        )

    def setUp(self):
        self.client.force_authenticate(self.owner_user)
        self.market, _ = Market.objects.get_or_create(
            marketer=self.owner_user.marketer,
            name="test"
        )


class MarketOwnerCreateViewTest(BaseMarketOwnerTest):
    """
    for anonymous user, cannot be written
    because written by RestFramework
    """

    def test_has_permission(self):
        self.assertEqual((permissions.IsAuthenticated, IsMarketer), MarketOwnerCreateView.permission_classes)

    def test_successful_request(self):
        response = self.client.post(
            reverse('market_owner:create'),
            data={
                "name": "test_2"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "test_2")
        self.assertEqual(Market.objects.count(), 2)

    def test_already_exist_market(self):
        data = {"name": "same_market"}
        response = self.client.post(
            reverse('market_owner:create'),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            reverse('market_owner:create'),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('Market already exists', response.data['error'])


class MarketOwnerUpdateViewTest(BaseMarketOwnerTest):

    def test_has_permission(self):
        self.assertCountEqual(
            (permissions.IsAuthenticated, IsMarketOwner),
            MarketOwnerUpdateView.permission_classes
        )

    def test_dose_not_exist_market(self):
        response = self.client.patch(
            reverse('market_owner:update', args=[uuid4()]),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_request(self):
        response = self.client.patch(
            reverse('market_owner:update', args=[self.market.id]),
            data={
                "name": "changed name"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), "changed name")


class MarketOwnerDeleteViewTest(BaseMarketOwnerTest):

    def test_has_permission(self):
        self.assertCountEqual(
            (permissions.IsAuthenticated, IsMarketOwner),
            MarketOwnerDeleteView.permission_classes
        )

    def test_dose_not_exist_market(self):
        response = self.client.delete(
            reverse('market_owner:delete', args=[uuid4()]),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_request(self):
        response = self.client.delete(
            reverse('market_owner:delete', args=[self.market.id]),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Market.objects.count(), 0)


class OwnerDetailViewTest(BaseMarketOwnerTest):
    def test_has_permission(self):
        self.assertCountEqual(
            (permissions.IsAuthenticated, IsMarketOwner),
            MarketOwnerDetailView.permission_classes
        )

    def test_dose_not_exist_market(self):
        response = self.client.get(
            reverse('market_owner:detail', args=[uuid4()]),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_request(self):
        response = self.client.get(
            reverse('market_owner:detail', args=[self.market.id]),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), "test")
        self.assertEqual(Market.objects.count(), 1)


class OwnerListViewTest(BaseMarketOwnerTest):
    def test_has_permission(self):
        self.assertCountEqual(
            (permissions.IsAuthenticated, IsMarketer),
            MarketOwnerListView.permission_classes
        )

    def test_successful_request(self):
        response = self.client.get(
            reverse('market_owner:list'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get("name"), "test")


class OtherOwnerTest(BaseMarketOwnerTest):

    def test_views_call_check_object_permissions(self):
        tests = {
            "apps.market.views.owner_views.MarketOwnerUpdateView.check_object_permissions": (
                "market_owner:update",
                "patch",
                MarketOwnerUpdateView,
            ),
            "apps.market.views.owner_views.MarketOwnerDeleteView.check_object_permissions": (
                "market_owner:delete",
                "delete",
                MarketOwnerDeleteView,
            ),
            "apps.market.views.owner_views.MarketOwnerDetailView.check_object_permissions": (
                "market_owner:detail",
                "get",
                MarketOwnerDetailView,
            ),
        }

        for method_path, (url_name, http_method, view_cls) in tests.items():
            self.setUp()
            with patch(method_path) as mock_method:
                url = reverse(url_name, args=[self.market.id])

                request = getattr(self.factory, http_method)(url)
                test.force_authenticate(request, self.owner_user)

                response = view_cls.as_view()(
                    request,
                    market_id=self.market.id
                )

                self.assertTrue(response.status_code < 500)

                # ✅ called once
                mock_method.assert_called_once()


class BaseMarketUserTest(test.APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            phone="09123456789"
        )
        self.owner_user = User.objects.create(
            phone="09135557788"
        )
        Marketer.objects.create(
            user=self.owner_user,
        )
        self.market_active, _ = Market.objects.get_or_create(
            marketer=self.owner_user.marketer,
            name="test_market"
        )
        self.market_dont_active, _ = Market.objects.get_or_create(
            marketer=self.owner_user.marketer,
            is_active=False,
            name="test_market_dont_active"
        )
        self.client.force_authenticate(self.user)


class UserListViewTest(BaseMarketUserTest):

    def test_successful_request(self):
        response = self.client.get(
            reverse('market_user:list'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class UserDetailViewTest(BaseMarketUserTest):
    def test_dose_not_exist_market(self):
        response = self.client.get(
            reverse('market_user:detail', args=[uuid4()]),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_is_not_active_market(self):
        response = self.client.get(
            reverse('market_user:detail', args=[self.market_dont_active.id]),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_request(self):
        response = self.client.get(
            reverse('market_user:detail', args=[self.market_active.id]),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
