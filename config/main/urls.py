from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, ActivateAccountView, LoginView, HouseViewSet, ApartmentViewSet, BookApartmentView, CancelBookingView, BookingView

router = DefaultRouter()
router.register('houses', HouseViewSet)
router.register('apartments', ApartmentViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/', ActivateAccountView.as_view(), name='activate-account'),
    path('login/', LoginView.as_view(), name='login'),
    path('book-apartment/<int:pk>/', BookApartmentView.as_view(), name='book-apartment'),
    path('cancel-booking/<int:pk>/', CancelBookingView.as_view(), name='cancel-booking'),
    path('booking/', BookingView.as_view(), name='booking'),

    path('', include(router.urls)),
]
