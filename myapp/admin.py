from .models import *
from django import forms
from django.contrib import admin
from .models import Notification
from .forms import NotificationForm
from django.contrib import messages
from django.contrib.auth.models import User

@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "image", "content"]

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "message"]


@admin.register(HotelReviewFine)
class HotelReviewFineAdmin(admin.ModelAdmin):
    list_display = ('reviewer_name', 'hotel_name', 'rating', 'date_posted', 'is_fake')
    list_filter = ('hotel_name', 'rating', 'is_fake')
    search_fields = ('reviewer_name', 'hotel_name', 'review_text')
    readonly_fields = ('date_posted',)  # Date posted should be read-only


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "consumer", "comment", "rating"]

class NotificationForm(forms.ModelForm):
    send_to_all = forms.BooleanField(required=False, label='Send to all users', initial=False)

    class Meta:
        model = Notification
        fields = ['user', 'message', 'send_to_all']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "created_at"]
    form = NotificationForm

    def add_view(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = NotificationForm(request.POST)
            if form.is_valid():
                user_id = form.cleaned_data['user']
                message = form.cleaned_data['message']
                send_to_all = form.cleaned_data['send_to_all']

                if send_to_all:
                    users = User.objects.all()
                    for user in users:
                        Notification.objects.create(user=user, message=message)
                    messages.success(request, 'Notification sent to all users.')
                else:
                    user = User.objects.get(id=user_id)
                    Notification.objects.create(user=user, message=message)
                    messages.success(request, 'Notification sent successfully.')

        return super().add_view(request, *args, **kwargs)
