from rest_framework import views, status
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
    permission_classes = (IsMarketer,)

    def post(self, request):
        self.check_permissions(request)

        serializer = self.serializer_class(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save(marketer=request.user.marketer)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

class MarketOwnerUpdateView(views.APIView):
    serializer_class = MarketOwnerSerializer
    permission_classes = (IsMarketOwner,)

    def patch(self, request,market_id):

        try :
            market = Market.objects.get(id=market_id)
        except Market.DoesNotExist:
            return Response(
                data={
                    "message": "Market does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, market)

        serializer = self.serializer_class(instance=market,data=request.data,partial=True)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class MarketOwnerDeleteView(views.APIView):
    serializer_class = MarketOwnerSerializer
    permission_classes = (IsMarketOwner,)

    def delete(self, request,market_id):
        try :
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
    permission_classes = (IsMarketOwner,)

    def get(self,request,market_id):
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
    permission_classes = (IsMarketer,)

    def get(self,request):
        self.check_permissions(request)

        markets = Market.objects.filter(marketer__user=request.user)

        serializer = MarketOwnerSerializer(instance=markets,many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )