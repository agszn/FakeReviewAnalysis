from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Consumer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Student Name")
    email = models.EmailField(max_length=277, verbose_name="Student Email")
    image = models.ImageField(upload_to='consumer_images/', null=True, blank=True, verbose_name="Consumer Image")
    content = models.TextField(verbose_name="Consumer Content", blank=True, null=True)

    def __str__(self):
        return str(self.id)

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name


class Review(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f'Review for {self.consumer.name}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message}"


class Hotel(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    description = models.CharField(max_length=100)  
    created_at = models.DateTimeField(auto_now_add=True)

class HotelReview(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=100)
    review_text = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    date_posted = models.DateTimeField(auto_now_add=True)
    is_fake = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.reviewer_name} - {self.hotel.name}"


class HotelReviewFine(models.Model):
    reviewer_name = models.CharField(max_length=100)
    review_text = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    date_posted = models.DateTimeField(auto_now_add=True)
    is_fake = models.BooleanField(default=False) 
    hotel_name = models.CharField(max_length=100,null=True, blank=True)  # New field for hotel name

    def __str__(self):
        return f"Review by {self.reviewer_name} for {self.hotel_name} - Rating: {self.rating}"
