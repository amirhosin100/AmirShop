from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.user.models import User
from apps.user.serializer.user_detail import UserDetailSerializer
from rest_framework.response import Response


class UserDetailView(APIView):
    serializer_class = UserDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, phone):

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            data = {
                "error": "user dose not exist"
            }
            return Response(
                data,
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserDetailSerializer(instance=user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
