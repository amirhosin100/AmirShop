from rest_framework.views import APIView

from apps.market_request.models import MarketRequest
from apps.market_request.serializer import (
    MarketRequestSerializer,
)
from utils.response import AResponse

# Create your views here.

class MarketRequestCreateView(APIView):
    serializer_class = MarketRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            return AResponse(serializer.data).success_create

        return AResponse(serializer.errors).bad_request

class MarketRequestDetailView(APIView):
    serializer_class = MarketRequestSerializer

    def get(self,request,market_request_id):

        market_request = MarketRequest.objects.get(pk=market_request_id)

        if market_request.user != request.user:
            data = {
                "error":"you have not permission to view this market request"
            }
            return AResponse(data).forbidden

        serializer = self.serializer_class(instance=market_request)

        return AResponse(serializer.data).success_ok


class MarketRequestListView(APIView):
    serializer_class = MarketRequestSerializer

    def get(self,request):
        market_requests = MarketRequest.objects.filter(user=request.user)

        serializer = self.serializer_class(market_requests, many=True)

        return AResponse(serializer.data).success_ok

