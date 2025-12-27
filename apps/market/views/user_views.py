from rest_framework import views, status
from rest_framework.response import Response

from apps.market.models import Market
from apps.market.serializer.market_serializer import (
    MarketUserSerializer
)


class AllMarketsView(views.APIView):
    serializer_class = MarketUserSerializer

    def get(self, request):
        markets = Market.objects.filter(is_active=True)

        serializer = self.serializer_class(instance=markets, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class MarketDetailView(views.APIView):
    serializer_class = MarketUserSerializer

    def get(self, request, market_id):
        try:
            market = Market.objects.get(id=market_id, is_active=True)
        except Market.DoesNotExist:
            return Response(
                data={
                    "message": "Market does not exist"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(instance=market)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
