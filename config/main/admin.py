from django.contrib import admin
from .models import House, Apartment

class ApartmentInline(admin.TabularInline):
    model = Apartment
    extra = 1

class HouseAdmin(admin.ModelAdmin):
    # list_display указывает поля, которые будут отображаться в списке домов.
    list_display = ('address', 'owner', 'description')
    # search_fields указывает поля, по которым можно будет искать дома.
    search_fields = ('address', 'owner__username')
    # inlines добавляет инлайн - модель ApartmentInline, что позволяет
    inlines = [ApartmentInline]

class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('house', 'number_of_rooms', 'floor', 'is_booked', 'booked_by')
    list_filter = ('house', 'number_of_rooms', 'floor', 'is_booked')
    search_fields = ('house__address', 'booked_by__username')

admin.site.register(House, HouseAdmin)
admin.site.register(Apartment, ApartmentAdmin)

# Register your models here.
