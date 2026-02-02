from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import views, status
from rest_framework.response import Response
from apps.market.services import MarketService
from apps.market.models import Market
from apps.market.serializer.market_serializer import (
    MarketUserSerializer
)


class AllMarketsView(views.APIView):
    serializer_class = MarketUserSerializer

    def get(self, request):
        page = request.GET.get("page", 1)
        data = MarketService.load_market_list(page)

        if not data:
            markets = Market.objects.filter(is_active=True)
            paginator = Paginator(markets, 10)

            try:
                markets = paginator.page(page)
            except PageNotAnInteger:
                return Response(
                    data={
                        "error": "Page not an integer"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except EmptyPage:
                return Response(
                    data={
                        "error": "Page is empty"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = MarketUserSerializer(markets, many=True)
            data = {
                "page": page,
                "count": paginator.num_pages,
                "data": serializer.data,
            }
            # save in cache
            MarketService.save_market_list(data, page)

        return Response(
            data=data,
            status=status.HTTP_200_OK
        )


class MarketDetailView(views.APIView):
    serializer_class = MarketUserSerializer

    def get(self, request, market_id):
        data = MarketService.load_market_detail(market_id)

        if not data:
            try:
                market = Market.objects.get(id=market_id,is_active=True)
            except Market.DoesNotExist:
                return Response(
                    data={
                        "message": "Market does not exist"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = MarketUserSerializer(instance=market)
            data = serializer.data
            MarketService.save_market_detail(data,market_id)

        return Response(
            data,
            status=status.HTTP_200_OK,
        )
