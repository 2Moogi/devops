import json

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.mail import EmailMessage
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import AuthenticationFailed
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import base64

from .models import Account, RegisterCodeBuffer
from todo.models import Todo, ColorPriority, PriorityName
from .serializers import RegisterSerializer, LoginSerializer, UpdateSerializer, ChangePasswordSerializer
from .security import create_email_code

import base64

#추가
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from django.contrib.auth.views import PasswordResetConfirmView,PasswordResetCompleteView

#가입
class RegisterView(APIView):
    @swagger_auto_schema(
        operation_summary="회원가입",
        manual_parameters=[
            openapi.Parameter(
                'nickname',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 닉네임'
            ),
            openapi.Parameter(
                'email',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 이메일'
            ),
            openapi.Parameter(
                'password',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 패스워드'
            ),
        ],
        responses={
            200: openapi.Response(
                description="회원가입성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                        'account': openapi.Schema(type=openapi.TYPE_OBJECT,
                            properties={
                                'nickname': openapi.Schema(type=openapi.TYPE_STRING, description="회원가입에 성공한 닉네임"),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, description="회원가입에 성공한 이메일"),
                        }),
                        
                    },         
                ),
            ),
            500: openapi.Response(
                description="회원가입실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                        'account': openapi.Schema(type=openapi.TYPE_STRING, description="Null값")
                    },
                ),
            ),
        },
     )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "account": serializer.data,
                    "resultCode": 200,
                    },
                status=status.HTTP_200_OK,
            )
        return Response({"resultCode":500, "account":None}, status=status.HTTP_400_BAD_REQUEST)

#회원탈퇴
class WithdrawalView(APIView):
    @swagger_auto_schema(
        operation_summary="회원탈퇴",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
        ],
        responses={
            200: openapi.Response(
                description="탈퇴성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },         
                ),
            ),
            500: openapi.Response(
                description="탈퇴실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },
                ),
            ),
        },
     )
    def delete(self, request):
        user = request.user
        #사용자데이터수집
        todo = Todo.objects.filter(writer=user.email)
        color_pri = ColorPriority.objects.filter(writer=user.email)
        pri_name = PriorityName.objects.filter(writer=user.email)
        
        #사용자데이터 전체삭제
        if user.image:
                user.image.delete()
        todo.delete()
        color_pri.delete()
        pri_name.delete()
        #사용자삭제
        user.delete()
        
        resultCode = 200
        return Response({"resultCode":resultCode})

#로그인
class LoginView(APIView):
    @swagger_auto_schema(
        operation_summary="로그인",
        manual_parameters=[
            openapi.Parameter(
                'email',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 이메일'
            ),
            openapi.Parameter(
                'password',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 패스워드'
            ),
        ],
        responses={
            200: openapi.Response(
                description="로그인성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                        'account': openapi.Schema(type=openapi.TYPE_OBJECT,
                            properties={
                                'token' : openapi.Schema(type=openapi.TYPE_STRING, description="로그인에 성공한 토큰"),
                                'nickname': openapi.Schema(type=openapi.TYPE_STRING, description="로그인에 성공한 닉네임"),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, description="로그인에 성공한 이메일"),
                                'image' : openapi.Schema(type=openapi.TYPE_STRING, description="로그인에 성공한 이미지"),
                        }),
                        
                    },         
                ),
            ),
            500: openapi.Response(
                description="로그인실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                        'token': openapi.Schema(type=openapi.TYPE_STRING, description="Null값"),
                        'nickname': openapi.Schema(type=openapi.TYPE_STRING, description="Null값"),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description="Null값"),
                        'image': openapi.Schema(type=openapi.TYPE_STRING, description="Null값"),
                    },
                ),
            ),
        },
     )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        result = serializer.validated_data
        
        if "Login Error" == result:
            return Response({"resultCode":500, "token":None, "nickname":None, "email":None, "image":None}, status=status.HTTP_200_OK)
        
        login_data = result
        return Response(dict({"resultCode":200}, **login_data), status=status.HTTP_200_OK)
    
#로그아웃
class LogoutView(APIView):
    @swagger_auto_schema(
        operation_summary="로그아웃",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
        ],
        responses={
            200: openapi.Response(
                description="로그아웃 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
        },
     )
    def post(self, request):
        request.user.auth_token.delete()
        return Response(dict({"resultCode":200}), status=status.HTTP_200_OK)

#토큰으로 사용자 정보 조회
class WhoView(APIView):
    @swagger_auto_schema(
        operation_summary="토큰으로 사용자 정보 조회",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
        ],
        responses={
            200: openapi.Response(
                description="조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                        'nickname': openapi.Schema(type=openapi.TYPE_STRING, description="해당 토큰 닉네임"),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description="해당 토큰 이메일"),
                        'image': openapi.Schema(type=openapi.TYPE_STRING, description="해당 토큰 프로필 사진"),
                    },
                ),
            ),
            500: openapi.Response(
                description="조회 실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
        },
     )
    def get(self, request):
        try:
            token = request.auth
        except Token.DoesNotExist:
            print("This")
            raise AuthenticationFailed('Custom message: Invalid token.')
            #return Response({"resultCode":500, "nickname":None, "email":None, "image":None})
        
        user = request.user #Account객체
        nickname = user.nickname #Account.nickname
        email = user.email #Account.email

        #사진이 없거나, 못찾을경우 에외처리
        try:
            image = user.image #Account.image
            return_image = base64.b64encode(image.read())
        except: 
            image = None
            return_image = None

        return Response({"resultCode":200, "nickname":str(nickname), "email":str(email), "image":return_image}, status=status.HTTP_200_OK)
    
#토큰유효성검사
class TokenCheckView(APIView):
    @swagger_auto_schema(
        operation_summary="토큰유효성검사",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
        ],
        responses={
            200: openapi.Response(
                description="유효한토큰",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },
                ),
            ),
            500: openapi.Response(
                description="유효하지않은토큰",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
        },
     )
    def get(self, request):
        try:
            token = request.auth
        except Token.DoesNotExist:
            return Response({"resultCode":500})
        return Response({"resultCode":200})

#EmailCode받기
class EmailCodeView(APIView):
    @swagger_auto_schema(
        operation_summary="이메일로 인증번호 받기",
        manual_parameters=[
            openapi.Parameter(
                'Email',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 이메일'
            ),
        ],
        responses={
            200: openapi.Response(
                description="인증코드 전송 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
        },
     )
    def get(self, request): #코드전송 및 중복가입검사
        email = request.GET['email']
        
        #중복여부
        res = Account.objects.filter(email=email)
        if len(res) > 0:
            return Response({"resultCode":500}, status=status.HTTP_200_OK)
        
        #인증코드 전송
        mail_code = create_email_code()
        mail_send = EmailMessage(
            "Group TODO 인증코드 발송",
            "인증코드: "+mail_code,
            to=[email],
        )
        
        #인증코드&이메일 저장
        buffer = RegisterCodeBuffer.objects.filter(email=email)
        if len(buffer) > 0:
            buffer.update(code=mail_code)
        else:
            RegisterCodeBuffer.objects.create(email=email, code=mail_code)
            
        mail_send.send()
        return Response({"resultCode":200}, status=status.HTTP_200_OK)
    
    
    #post
    #인증코드 and 이메일 일치 여부 확인
    @swagger_auto_schema(
        operation_summary="이메일로 인증번호 확인하기",
        manual_parameters=[
            openapi.Parameter(
                'Email',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 이메일'
            ),
            openapi.Parameter(
                'code',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='이메일로 온 코드'
            ),
        ],
        responses={
            200: openapi.Response(
                description="인증코드 일치",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            500: openapi.Response(
                description="인증코드 불일치",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
        },
     )
    def post(self, request):
        data = json.loads(request.body)
        
        email = data["email"]
        code = data["code"]
        
        try:
            target = RegisterCodeBuffer.objects.get(email=str(email))
            if target.code == int(code):
                return Response({"resultCode":200}, status=status.HTTP_200_OK)
        except:
            pass
        return Response({"resultCode":500}, status=status.HTTP_200_OK)

    
class EditAccountView1(APIView):
    @swagger_auto_schema(
        operation_summary="프로필사진 및 닉네임 수정",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
            openapi.Parameter(
                'nickname',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='변경할 닉네임'
            ),
            openapi.Parameter(
                'image',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='변경할 프로필사진'
            ),
            openapi.Parameter(
                'imdel',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='기본이미지변경=true, 아니라면=false'
            ),
        ],
        responses={
            200: openapi.Response(
                description="회원정보수정 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT,
                            properties={
                                'nickname': openapi.Schema(type=openapi.TYPE_STRING, description="변경된 닉네임"),
                                'image': openapi.Schema(type=openapi.TYPE_STRING, description="사진 변경했다면 encoding값, 없다면 null값"),
                        }),
                        
                    },         
                ),
            ),
            500: openapi.Response(
                description="회원정보수정 실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드")
                    },
                ),
            ),
        },
     )
    def post(self, request): #닉네임, 프로필 사진 수정
        user = request.user
        Account_model = Account.objects.get(email=str(user.email))
        
        data = {}
        if "nickname" in request.POST:
            data["nickname"] = request.POST["nickname"]
        if request.POST["imdel"] == "true": #이미지 삭제
            Account_model.image.delete()
        elif "image" in request._request.FILES:
            if Account_model.image is not None: #이미지 중복 업로드 방지(기존 이미지 삭제)
                Account_model.image.delete()
                
            data["image"] = request._request.FILES["image"]
            
            fe = data["image"].name.split(".")[1]
            data["image"].name = str(user.email)+"."+str(fe)
        
        serializer = UpdateSerializer.update(instance=Account_model, validate_data=data)
        
        if not serializer.image:
            return Response({"resultCode":200, "data":{"nickname":serializer.nickname, "image":None}})
        return Response({"resultCode":200, "data":{"nickname":serializer.nickname, "image":base64.b64encode(serializer.image.read())}})

class EditAccountView2(APIView):
    @swagger_auto_schema(
        operation_summary="비밀번호 변경",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
            openapi.Parameter(
                'originpw',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='기존에 사용하던 비밀번호'
            ),
            openapi.Parameter(
                'newpw',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='새로운 비밀번호'
            ),
        ],
        responses={
            200: openapi.Response(
                description="비밀번호 변경 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            500: openapi.Response(
                description="비밀번호 변경 실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
        },
     )
    def post(self, request): #패스워드 수정
        user = Account.objects.get(email=str(request.user.email))
        
        origin_password = request.data["originpw"]
        new_password = request.data["newpw"]
        
        serializer = ChangePasswordSerializer()
        data={}
        data["old_password"] = origin_password
        data["new_password"] = new_password
        
        if serializer.validate_new_password(new_password):
            if serializer.update(instance=user, validated_data=data):        
                resultCode = 200
                print("SUCCESS")
                return Response({"resultCode":resultCode})
            resultCode = 500
            print("Failed: update")
            return Response({"resultCode":resultCode})
        else:
            resultCode = 500
            print("Failed: validate new password")
            return Response({"resultCode":resultCode})
        
class FindPasswordView(APIView):
    @swagger_auto_schema(
        operation_summary="비밀번호 찾기",
        manual_parameters=[
            openapi.Parameter(
                'email',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 이메일'
            ),
    ],
        responses={
            200: openapi.Response(
                description="이메일 발송 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },
                ),
            ),
            500: openapi.Response(
                description="존재하지 않는 계정",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },
                ),
            ),
        },
    )
    def get(self,request):
        email = request.GET['email']
        is_duplicate = Account.objects.filter(email=email).exists() 
        
        if is_duplicate:
            user = Account.objects.get(email=email)
            url = reverse('password_reset_confirm', kwargs={
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                })
            url_with_timeout = f"{request.build_absolute_uri(url)}?timeout={settings.PASSWORD_RESET_TIMEOUT}"
            mail_body = f"비밀번호 재설정 링크 : {url_with_timeout}"

            mail_send = EmailMessage(
                "Group TODO 비밀번호 재설정 링크 발송",
                mail_body,
                to=[email]
            )
            mail_send.send()
            return Response({"resultCode":200}, status=status.HTTP_200_OK)
        else:
            return Response({"resultCode":500}, status=status.HTTP_200_OK)
        
        
        
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'