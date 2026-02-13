import logging
from rest_framework import views, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from apps.user.models import User, OTP
from rest_framework.response import Response
from apps.user.serializer.user_registration import (
    UserRegisterSerializer,
    UserSetPasswordSerializer,
    UserInformationSerializer
)

logger = logging.getLogger(__name__)


class UserRegistrationCreateCodeView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data['phone']

            try:
                otp = OTP.codes.create_code(phone=phone)
            except ValueError as e:
                return Response(
                    data={
                        'error': str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            code = otp.code

            data = {
                "code": code,
                "mobile_number": phone,
            }

            logger.info(f'created code for {phone}')

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

                try:
                    check = OTP.codes.check_code(phone, code)
                except ValueError as e:
                    logger.warning(f'code is incorrect. phone number is {phone}')
                    return Response(
                        data={
                            "error": str(e)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if check :
                    user, is_user_create = User.objects.get_or_create(phone=phone)
                    token, _ = Token.objects.get_or_create(user=user)

                    refresh = RefreshToken.for_user(user)

                    # set_unusable_pass
                    if is_user_create:
                        user.set_unusable_password()
                        user.save()

                    response_data = {
                        "mobile_number": phone,
                        "token": token.key,
                        "jwt" : {
                            "refresh": str(refresh),
                            "access" : str(refresh.access_token)
                        }
                    }

                    logger.info(f'created token for {phone}')

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
            logger.info(f'password have been updated . Phone number is {request.user.phone}.')

            return Response(
                success_data,
                status=status.HTTP_200_OK
            )
        else:
            logger.info(f"password didn't change. User id is {request.user.id}.")
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
            try:
                check = OTP.codes.check_code(phone, code)
            except ValueError as e:
                logger.warning(f"password didn't reset. User id is {request.user.id}.")
                return Response(
                    data={
                        "error": str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if check:
                request.user.set_unusable_password()
                request.user.save()

                data = {
                    'success': True,
                    'message': "password has been reset!",
                }
                logger.info(f'password has been reset . Phone number is {request.user.phone}.')
                return Response(
                    data,
                    status=status.HTTP_200_OK
                )
        else:
            data = {
                'error': 'code is empty',
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
