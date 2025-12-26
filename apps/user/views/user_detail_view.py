from rest_framework.views import APIView
from apps.user.models import User
from apps.user.serializer.user_detail import UserDetailSerializer
from utils.response import AResponse


class UserDetailView(APIView):
    serializer_class = UserDetailSerializer

    def get(self, request, phone):

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            data = {
                "error": "user dose not exist"
            }
            return AResponse(data).not_found

        serializer = UserDetailSerializer(instance=user)

        return AResponse(serializer.data).success_ok
