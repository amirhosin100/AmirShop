from rest_framework import test, status
from django.urls import reverse
from apps.market_request.models import MarketRequest
from apps.user.models import User
from uuid import uuid4


class BaseTest(test.APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            phone='09123456789',
        )
        cls.other_user = User.objects.create_user(
            phone='09123456788',
        )
        cls.factory = test.APIRequestFactory()
        cls.list_url = reverse('market_request:list')
        cls.create_url = reverse('market_request:create')
        cls.detail_url = lambda m_id: reverse('market_request:detail', kwargs={'market_request_id': m_id})

    def setUp(self):
        self.data = {
            "mobile_number": "09123456789",
            "city": "test_city",
            "province": "province",
            "address": f"{'address' * 5}",
            "description": f"{'description_' * 10}",
            "national_code": f"1234567890",
            "age":30,
        }
        self.market_request_example = MarketRequest.objects.create(
            user=self.user,
            **self.data,
        )


class MarketRequestListViewTest(BaseTest):
    def test_by_anonymous_user(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_by_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['city'], "test_city")

    def test_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_remove_object(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.market_request_example.delete()

        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 0)


class MarketRequestDetailViewTest(BaseTest):

    def test_by_anonymous_user(self):
        response = self.client.post(self.detail_url(self.market_request_example.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.detail_url(self.market_request_example.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("you have not permission ", response.data['error'])

    def test_by_owner_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.market_request_example.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for field, value in self.data.items():
            self.assertEqual(value, response.data[field])

    def test_not_found(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'MarketRequest does not exist')


class MarketRequestCreateViewTest(BaseTest):

    def test_by_anonymous_user(self):
        response = self.client.post(
            self.create_url,
            data=self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_by_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(MarketRequest.objects.count(), 2)

    def test_bad_request(self):
        self.data['address'] = "bad_address"

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_url, self.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
