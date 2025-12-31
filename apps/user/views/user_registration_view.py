from rest_framework import views, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from core.manage_code import CodeManager
from apps.user.models import User
from rest_framework.response import Response
from apps.user.serializer.user_registration import (
    UserRegisterSerializer,
    UserSetPasswordSerializer,
    UserInformationSerializer
)


class UserRegistrationCreateCodeView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            user_code = CodeManager(request, phone)
            code = user_code.generate_code()

            data = {
                "code": code,
                "mobile_number": phone,
            }

            return Response(
                data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserVerifyCodeView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        code = request.data.get("code")
        if code:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                phone = serializer.validated_data['phone']
                user_code = CodeManager(request, phone)

                if user_code.load_code():
                    if user_code.check_code(code):
                        user, is_user_create = User.objects.get_or_create(phone=phone)
                        token, _ = Token.objects.get_or_create(user=user)

                        #set_nuusable_pass
                        if is_user_create:
                            user.set_unusable_password()
                            user.save()

                        response_data = {
                            "mobile_number": phone,
                            "token": token.key
                        }

                        return Response(
                            response_data,
                            status=status.HTTP_201_CREATED
                        )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                data={
                    'error': 'code is empty'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            data={
                'error': 'code is incorrect or expired'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UserSetPasswordView(views.APIView):
    serializer_class = UserSetPasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        success = False
        # first_change
        if not request.user.has_usable_password():

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.update(request.user, serializer.validated_data)
                success = True
                print("yes")

        else:
            old_password = request.data.get('old_password')
            if request.user.check_password(old_password) and old_password:
                serializer = self.serializer_class(data=request.data)
                if serializer.is_valid():
                    serializer.update(request.user, serializer.validated_data)
                    success = True

            else:
                return Response(
                    data={
                        'error': 'old_password is not correct'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if success:
            success_data = {
                'message': 'password have been updated!'
            }

            return Response(
                success_data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def options(self, request, *args, **kwargs):
        data = {
            "data": [
                "password",
                "password2",
            ]
        }
        if request.user.password:
            data['data'].append("old_password")

        return Response(
            data,
            status=status.HTTP_200_OK
        )


class UserPasswordResetView(views.APIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = UserRegisterSerializer

    def post(self, request):

        code = request.data.get("code")
        if code:
            phone = request.user.phone
            user_code = CodeManager(request, phone)
            if user_code.load_code():
                if user_code.check_code(code):
                    request.user.set_unusable_password()
                    request.user.save()

                    data = {
                        'success': True,
                        'message': "password has been reset!",
                    }
                    return Response(
                        data,
                        status=status.HTTP_200_OK
                    )

        data = {
            'error': 'code is incorrect or expired',
        }
        return Response(
            data,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserChangeInfoView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserInformationSerializer

    def patch(self, request):
        serializer = self.serializer_class(
            data=request.data,
            partial=True,
            instance=request.user
        )
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
