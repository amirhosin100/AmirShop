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
        serializer = MarketRequestSerializer(data=request.data)

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

        try:
            market_request = MarketRequest.objects.get(id=market_request_id)
        except MarketRequest.DoesNotExist:
            return Response(
                data={
                    'error':'MarketRequest does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if market_request.user != request.user:
            data = {
                "error":"you have not permission to view this market request"
            }
            return Response(
                data,
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MarketRequestSerializer(instance=market_request)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class MarketRequestListView(APIView):
    serializer_class = MarketRequestSerializer

    def get(self,request):
        market_requests = MarketRequest.objects.filter(user=request.user)

        serializer = MarketRequestSerializer(market_requests, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

