from rest_framework import views, status, permissions
from rest_framework.response import Response
from apps.market.models import Market
from apps.market.serializer.market_serializer import (
    MarketOwnerSerializer,
)
from permissions.market import (
    IsMarketOwner,
    IsMarketer
)


class MarketOwnerCreateView(views.APIView):
    serializer_class = MarketOwnerSerializer
    permission_classes = (permissions.IsAuthenticated, IsMarketer)

    def post(self, request):
        serializer = MarketOwnerSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        market_name = serializer.validated_data['name']

        if request.user.marketer.markets.filter(name=market_name).exists():
            return Response(
                data={
                    "error": "Market already exists"
                },
                status=status.HTTP_409_CONFLICT
            )

        serializer.save(marketer=request.user.marketer)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class MarketOwnerUpdateView(views.APIView):
    serializer_class = MarketOwnerSerializer
    permission_classes = (IsMarketOwner, permissions.IsAuthenticated,)

    def patch(self, request, market_id):

        try:
            market = Market.objects.get(id=market_id)
        except Market.DoesNotExist:
            return Response(
                data={
                    "message": "Market does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, market)

        serializer = self.serializer_class(instance=market, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class MarketOwnerDeleteView(views.APIView):
    serializer_class = MarketOwnerSerializer
    permission_classes = (permissions.IsAuthenticated, IsMarketOwner)

    def delete(self, request, market_id):
        try:
            market = Market.objects.get(id=market_id)
        except Market.DoesNotExist:
            return Response(
                data={
                    "message": "Market does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, market)

        market.delete()

        return Response(
            data={
                "message": "Market deleted"
            },
            status=status.HTTP_200_OK
        )


class MarketOwnerDetailView(views.APIView):
    serializer_class = MarketOwnerSerializer
    permission_classes = (permissions.IsAuthenticated, IsMarketOwner)

    def get(self, request, market_id):
        try:
            market = Market.objects.get(id=market_id)
        except Market.DoesNotExist:
            return Response(
                data={
                    "message": "Market does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, market)

        serializer = self.serializer_class(instance=market)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class MarketOwnerListView(views.APIView):
    serializer_class = MarketOwnerSerializer
    permission_classes = (permissions.IsAuthenticated, IsMarketer)

    def get(self, request):
        markets = Market.objects.filter(marketer__user=request.user)

        serializer = MarketOwnerSerializer(instance=markets, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
