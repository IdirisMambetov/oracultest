from .serializers import RegisterSerializer, ActivateAccountSerializer, LoginSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import House, Apartment
from .serializers import HouseSerializer, ApartmentSerializer

from django.urls import reverse
from django.contrib.auth.views import LoginView as AuthLoginView


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ActivateAccountView(generics.GenericAPIView):
    serializer_class = ActivateAccountSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Аккаунт успешно активирован'}, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        tokens = serializer.create(user)
        return Response(tokens, status=status.HTTP_200_OK)


class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ApartmentFilter(filters.FilterSet):
    number_of_rooms = filters.NumberFilter(field_name="number_of_rooms", label="Количество комнат")
    floor = filters.NumberFilter(field_name="floor", label="пол")

    class Meta:
        model = Apartment
        fields = ['number_of_rooms', 'floor']


class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = ApartmentFilter


class BookApartmentView(generics.UpdateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_booked:
            return Response({"detail": "Квартира уже забронирована."}, status=status.HTTP_400_BAD_REQUEST)

        instance.is_booked = True
        instance.booked_by = request.user
        instance.save()
        return Response({"detail": "Квартира успешно забронирована."}, status=status.HTTP_200_OK)


class CancelBookingView(generics.UpdateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_booked:
            return Response({"detail": "Квартира не забронирована."}, status=status.HTTP_400_BAD_REQUEST)

        if request.user != instance.booked_by and not request.user.is_staff:
            return Response({"detail": "У вас нет разрешения на отмену этого бронирования.."},
                            status=status.HTTP_403_FORBIDDEN)

        instance.is_booked = False
        instance.booked_by = None
        instance.save()
        return Response({"detail": "Бронирование успешно отменено."}, status=status.HTTP_200_OK)


class CustomLoginView(AuthLoginView):
    def get_success_url(self):
        return reverse('book-apartment', kwargs={'pk': self.request.user.pk})
