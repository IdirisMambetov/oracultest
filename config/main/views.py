from .serializers import RegisterSerializer, ActivateAccountSerializer, LoginSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import House, Apartment
from .serializers import HouseSerializer, ApartmentSerializer


from django.urls import reverse
from django.contrib.auth.views import LoginView as AuthLoginView



# 1
# Представление для регистрации пользователей.
# Использует CreateAPIView, которое предоставляет стандартное поведение для создания объектов
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

# 2
# Представление для активации аккаунта.
# Принимает POST-запрос, проверяет данные и активирует аккаунт.
class ActivateAccountView(generics.GenericAPIView):
    serializer_class = ActivateAccountSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Аккаунт успешно активирован'}, status=status.HTTP_200_OK)


# 3
# Представление для входа в систему.
# Принимает POST-запрос с данными для входа, проверяет их и возвращает токены для аутентификации.
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        tokens = serializer.create(user)
        return Response(tokens, status=status.HTTP_200_OK)

# 4
# ViewSet для работы с домами. Предоставляет стандартные CRUD операции.
# Доступно для аутентифицированных пользователей или для чтения без аутентификации.
class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# 5
# Фильтр для квартир, позволяет фильтровать по количеству комнат и этажу.
class ApartmentFilter(filters.FilterSet):
    number_of_rooms = filters.NumberFilter(field_name="number_of_rooms", label="Количество комнат")
    floor = filters.NumberFilter(field_name="floor", label="пол")

    class Meta:
        model = Apartment
        fields = ['number_of_rooms', 'floor']



# 6
# ViewSet для работы с квартирами. Предоставляет стандартные CRUD операции.
# Доступно для аутентифицированных пользователей или для чтения без аутентификации.
# Поддерживает фильтрацию по количеству комнат и этажу.
class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = ApartmentFilter


# 7
# Представление для бронирования квартиры. Проверяет,
# забронирована ли квартира, и если нет, бронирует её для текущего пользователя.
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


# 8
# Представление для отмены бронирования квартиры.
# Проверяет, забронирована ли квартира, и если да, снимает бронь.
# Пользователь должен быть тем, кто забронировал, или администратором.
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
        # Здесь можно указать URL, на который будет выполнено перенаправление после входа
        return reverse('book-apartment', kwargs={'pk': self.request.user.pk})
