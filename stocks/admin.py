from django.contrib import admin
from .models import Stock, StockHistory, ContactMessage, Subscriber

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "message", "created_at")
    search_fields = ("name", "email")

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at")
    search_fields = ("email",)

admin.site.register(Stock)
admin.site.register(StockHistory)
