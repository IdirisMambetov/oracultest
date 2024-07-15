from django.db import models
from django.contrib.auth.models import User

class House(models.Model):
    address = models.CharField("Адрес", max_length=255)
    owner = models.ForeignKey(User, verbose_name="Владелец", on_delete=models.CASCADE)
    description = models.TextField("Описание", null=True, blank=True)

    class Meta:
        verbose_name = "Дом"
        verbose_name_plural = "Дома"

    def __str__(self):
        return self.address

class Apartment(models.Model):
    house = models.ForeignKey(House, verbose_name="Дом", related_name='apartments', on_delete=models.CASCADE)
    number_of_rooms = models.IntegerField("Количество комнат")
    floor = models.IntegerField("Этаж")
    is_booked = models.BooleanField("Забронировано", default=False)
    booked_by = models.ForeignKey(User, verbose_name="Забронировано пользователем", null=True, blank=True, on_delete=models.SET_NULL, related_name='booked_apartments')

    class Meta:
        verbose_name = "Квартира"
        verbose_name_plural = "Квартиры"

    def __str__(self):
        return f'{self.house.address} - Кв. {self.id}'
