from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from .models import House, Apartment
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.is_active = False
        user.save()

        token = RefreshToken.for_user(user).access_token

        activation_link = f"http://yourdomain.com/activate/{str(token)}"
        send_mail(
            'активация аккаунта',
            f'Нажмите следующую ссылку, чтобы активировать свою учетную запись: {activation_link}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return user

class ActivateAccountSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            RefreshToken(value)
        except:
            raise serializers.ValidationError("Недействительный или просроченный токен")
        return value

    def save(self):
        token = self.validated_data['token']
        user = RefreshToken(token).user
        user.is_active = True
        user.save()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("Учетная запись пользователя не активирована.")
                return user
            else:
                raise serializers.ValidationError("Неверные логин или пароль.")
        else:
            raise serializers.ValidationError("Должен включать «имя пользователя» и «пароль»'.")

    def create(self, validated_data):
        user = validated_data
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = '__all__'

class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = '__all__'
