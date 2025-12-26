from rest_framework import views, permissions
from rest_framework.authtoken.models import Token
from core.manage_code import CodeManager
from apps.user.models import User
from utils.response import AResponse
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

            return AResponse(data).success_create
        else:
            return AResponse(serializer.errors).bad_request


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
                user_code.load_code()
                if user_code.check_code(code):

                    user, _ = User.objects.get_or_create(phone=phone)
                    token,_ = Token.objects.get_or_create(user=user)

                    response_data = {
                        "mobile_number": phone,
                        "token": token.key
                    }

                    return AResponse(response_data).success_create
                else:
                    return AResponse(
                        data={
                            'error': 'code is incorrect or expired'
                        }
                    ).bad_request
            else:
                return AResponse(serializer.errors).bad_request
        else:
            return AResponse(
                data={
                    'error': 'code is empty'
                }
            ).bad_request


class UserSetPasswordView(views.APIView):
    serializer_class = UserSetPasswordSerializer

    def post(self, request):
        success = False
        #first_change
        if not request.user.password :

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.update(request.user, serializer.validated_data)
                success = True
                print("yes")

        else :
            old_password = request.data.get('old_password')
            if request.user.check_password(old_password):
                serializer = self.serializer_class(data=request.data)
                if serializer.is_valid():
                    serializer.update(request.user, serializer.validated_data)
                    success = True

            else:
                return AResponse(
                    data={
                        'error': 'old_password is not correct'
                    }
                ).bad_request

        if success:
            success_data = {
                'message': 'password have been updated!'
            }

            return AResponse(success_data).success_ok
        else:
            return AResponse(serializer.errors).bad_request


    def options(self, request, *args, **kwargs):
        data = {
            "data": [
                "password",
                "password2",
            ]
        }
        if request.user.password :
            data['data'].append("old_password")

        return AResponse(data).success_ok


class UserPasswordResetView(views.APIView):
    permission_classes = [permissions.AllowAny]

    serializer_class = UserRegisterSerializer
    def post(self, request):

        code = request.data.get("code")
        if code:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                phone = serializer.validated_data['phone']
                user_code = CodeManager(request, phone)
                user_code.load_code()
                if user_code.check_code(code):
                    user = User.objects.get(phone=phone)
                    user.password = ""
                    user.save()

                    data = {
                        'success': True,
                        'message' : "password has been reset!",
                    }
                    return AResponse(data).success_create
            else:
                return AResponse(serializer.errors).bad_request

        data = {
            'code': 'code is incorrect or expired',
        }
        return AResponse(data).bad_request


class UserChangeInfoView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserInformationSerializer

    def patch(self, request):
        serializer = self.serializer_class(
            data=request.data,
            partial=True,
            instance=request.user
        )
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)

            return  AResponse(serializer.data).success_ok
        else:
            return AResponse(serializer.errors).bad_request
