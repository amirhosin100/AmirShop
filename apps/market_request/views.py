from rest_framework import status
from rest_framework.views import APIView

from apps.market_request.models import MarketRequest
from apps.market_request.serializer import (
    MarketRequestSerializer,
)
from rest_framework.response import Response

# Create your views here.

class MarketRequestCreateView(APIView):
    serializer_class = MarketRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class MarketRequestDetailView(APIView):
    serializer_class = MarketRequestSerializer

    def get(self,request,market_request_id):

        market_request = MarketRequest.objects.get(pk=market_request_id)

        if market_request.user != request.user:
            data = {
                "error":"you have not permission to view this market request"
            }
            return Response(
                data,
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.serializer_class(instance=market_request)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class MarketRequestListView(APIView):
    serializer_class = MarketRequestSerializer

    def get(self,request):
        market_requests = MarketRequest.objects.filter(user=request.user)

        serializer = self.serializer_class(market_requests, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

