from rest_framework import status
from rest_framework.response import Response

class AResponse:
    def __init__(self, data):
        self.data = data


    @property
    def success_ok(self):
        return Response(
            data=self._success_data,
            status=status.HTTP_200_OK
        )

    @property
    def success_create(self):
        return Response(
            data=self._success_data,
            status=status.HTTP_201_CREATED
        )

    @property
    def bad_request(self):
        return Response(
            self._fail_data,
            status=status.HTTP_400_BAD_REQUEST
        )

    @property
    def not_found(self):
        return Response(
            self._fail_data,
            status=status.HTTP_404_NOT_FOUND
        )

    @property
    def _success_data(self):
        return {
            "success": True,
            "data": self.data
        }

    @property
    def _fail_data(self):
        return {
            "success": False,
            "data": self.data
        }
