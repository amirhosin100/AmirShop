from django.contrib.auth.models import AnonymousUser
from rest_framework import test
from apps.market.models import Market
from apps.product.models import Product
from apps.user.models import User, Marketer
from permissions import market, product


class BasePermissionTest(test.APITestCase):
    """
    basic setup for all permissions
    """

    def setUp(self):
        self.factory = test.APIRequestFactory()
        self.request = self.factory.get('/')

    def set_user(self, user):
        self.request.user = user
        return True

    def has_success(self, user, permission, obj=None):
        self.set_user(user)
        if obj:
            self.assertTrue(permission.has_object_permission(self.request, None, obj))
        else:
            self.assertTrue(permission.has_permission(self.request, None))

    def has_failure(self, user, permission, obj=None):
        self.set_user(user)
        if obj:
            self.assertFalse(permission.has_object_permission(self.request, None, obj))
        else:
            self.assertFalse(permission.has_permission(self.request, None))


class PermissionTest(BasePermissionTest):
    """
    this class made for better management of permissions
    """
    normal_user = None
    owner_user = None
    anonymous_user = AnonymousUser()
    permission = None
    obj = None

    def is_owner_user(self):
        self.has_success(self.owner_user, self.permission, self.obj)

    def is_normal_user(self):
        self.has_failure(self.normal_user, self.permission, self.obj)

    def is_anonymous_user(self):
        self.has_failure(self.anonymous_user, self.permission, self.obj)

    def do_all(self):
        if self.normal_user and self.owner_user and self.permission:
            self.is_owner_user()
            self.is_anonymous_user()
            self.is_normal_user()


class IsMarketerTest(PermissionTest):
    permission = market.IsMarketer()

    @classmethod
    def setUpTestData(cls):
        cls.normal_user = User.objects.create_user(
            phone='09123456789'
        )

        cls.owner_user = User.objects.create_user(
            phone='09134445566'
        )

        Marketer.objects.create(
            user=cls.owner_user,
        )

    def test_all(self):
        self.do_all()


class IsMarketOwnerTest(IsMarketerTest):
    permission = market.IsMarketOwner()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.market = Market.objects.create(
            marketer=cls.owner_user.marketer,
            name='test_market',
        )
        cls.obj = cls.market


class IsProductOwnerTest(IsMarketOwnerTest):
    permission = product.IsProductOwner()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        #overide object
        cls.product = Product.objects.create(
            market=cls.market,
            name='product_test',
            price=100
        )
        cls.obj = cls.product