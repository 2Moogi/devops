from rest_framework import serializers
from .models import Account
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinLengthValidator
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token
import base64

#회원가입 시리얼라이저
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Account.objects.all())],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        max_length=16, 
        validators=[MinLengthValidator(8)],
    )
    # password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = ('nickname', 'password', 'email')
    # def validate(self, data):
    #     if data['password'] != data['password2']:
    #         raise serializers.ValidationError(
    #             {"password": "Password fields didn't match."})

    #     return data

    def create(self, validated_data):
        user = Account.objects.create_user(
            nickname=validated_data['nickname'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        user.save()
        return user

#로그인 시리얼라이저
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        required = True,
        write_only = True
    )
    password = serializers.CharField(
        required = True,
        write_only = True,
    )
    class Meta(object):
        model = Account
        fields = ('email', 'password')

    def validate(self, data):
        email = data.get('email',None)
        password = data.get('password',None)

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)

            if not user.check_password(password):
                return "Login Error"
        else:
            return "Login Error"
        token, created = Token.objects.get_or_create(user=user)
        #이미지 가져오기(에러처리)
        try:
            image = user.image #Account.image
            print(image)
            return_image = base64.b64encode(image.read())
        except: 
            image = None
            return_image = None
        data = {"token":str(Token.objects.get(user=user)), "nickname":user.nickname, "email":user.email, "image":return_image}
        
        return data

#회원정보수정 시리얼라이저(닉네임, 프로필사진)
class UpdateSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Account
        fields = ('nickname', 'image', 'is_staff', 'is_superuser')

    def update(instance, validate_data):
        instance.nickname = validate_data.get("nickname", instance.nickname)
        instance.image = validate_data.get("image", instance.image)

        instance.is_staff = instance.is_staff
        instance.is_superuser = instance.is_superuser
        
        instance.save()

        return instance

    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value)<8 or len(value)>16:
            return False
        return value

    def update(self, instance, validated_data):
        old_password = validated_data.get('old_password')
        new_password = validated_data.get('new_password')

        if not instance.check_password(old_password):
            return False
        
        instance.set_password(new_password)
        instance.save()
        
        return instance