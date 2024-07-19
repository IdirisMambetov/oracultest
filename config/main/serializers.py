from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from .models import Apartment, House


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
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        uid = attrs.get('uid')
        token = attrs.get('token')
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            raise serializers.ValidationError('Неверный uid или токен')

        if not user.is_active:
            user.is_active = True
            user.save()
        else:
            raise serializers.ValidationError('Аккаунт уже активирован')

        return attrs


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)

            if not user:
                raise serializers.ValidationError("Некорректные учетные данные")

            if not user.is_active:
                raise serializers.ValidationError("Этот аккаунт неактивен")

        else:
            raise serializers.ValidationError("Необходимо указать 'username' и 'password'")

        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
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


from rest_framework import serializers
from .models import Apartment, House

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment  # или House
        fields = ['is_booked', 'booked_by']

    def update(self, instance, validated_data):
        instance.is_booked = validated_data.get('is_booked', instance.is_booked)
        instance.booked_by = validated_data.get('booked_by', instance.booked_by)
        instance.save()
        return instance



