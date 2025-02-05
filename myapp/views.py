from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import *
from .models import *
from django.db.models import Q

from django.http import JsonResponse
from django.conf import settings
import os

import joblib
import numpy as np

def base(request):
    return render(request, 'base.html')

def about(request):
    return render(request, 'about/about.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            #create a new registration object and avoid saving it yet
            new_user = user_form.save(commit=False)
            #reset the choosen password
            new_user.set_password(user_form.cleaned_data['password'])
            #save the new registration
            new_user.save()
            return render(request, 'registration/register_done.html',{'new_user':new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html',{'user_form':user_form})

def profile(request):
    return render(request, 'profile/profile.html')



@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = EditProfileForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
    else:
        user_form = EditProfileForm(instance=request.user)
    
    return render(request, 'profile/edit_profile.html', {'user_form': user_form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Your account was successfully deleted.')
        return redirect('base')  # Redirect to the homepage or another page after deletion

    return render(request, 'registration/delete_account.html')
# das
@login_required
def dashboard(request):
    users_count = User.objects.all().count()
    consumers = Consumer.objects.all().count
    notify_users = Notification.objects.all().count()
    review_count = Review.objects.all().count()

    context = {
        'users_count':users_count,
        'consumers':consumers,
        'notify_users':notify_users,
        'review_count':review_count,
        'barData': [10, 20, 30],
        'lineData': [30, 25, 35],
        'pieData': [10, 40, 50],
        'scatterData': [{'x': 10, 'y': 20}, {'x': 15, 'y': 10}, {'x': 20, 'y': 30}],
        
    }
    return render(request, "dashboard/dashboard.html", context=context)
#CRUD operations start here
@login_required
def dashvalues(request):
    consumers = Consumer.objects.all()
    search_query = ""
    
    if request.method == "POST": 
        if "create" in request.POST:
            name = request.POST.get("name")
            email = request.POST.get("email")
            image = request.FILES.get("image")
            content = request.POST.get("content")

            Consumer.objects.create(
                name=name,
                email=email,
                image=image,
                content=content
            )
            messages.success(request, "Consumer added successfully")
    
        elif "update" in request.POST:
            id = request.POST.get("id")
            name = request.POST.get("name")
            email = request.POST.get("email")
            image = request.FILES.get("image")
            content = request.POST.get("content")

            consumer = get_object_or_404(Consumer, id=id)
            consumer.name = name
            consumer.email = email
            consumer.image = image
            consumer.content = content
            consumer.save()
            messages.success(request, "Consumer updated successfully")
    
        elif "delete" in request.POST:
            id = request.POST.get("id")
            Consumer.objects.get(id=id).delete()
            messages.success(request, "Consumer deleted successfully")
        
        elif "search" in request.POST:
            search_query = request.POST.get("query")
            consumers = Consumer.objects.filter(Q(name__icontains=search_query) | Q(email__icontains=search_query))

    context = {
        "consumers": consumers, 
        "search_query": search_query
    }
    return render(request, "crud/dashvalue.html", context=context)
# CRUD operations end here

# Contact start
@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for contacting us!")
            return redirect('dashboard')  # Redirect to the same page to show the modal
    else:
        form = ContactForm()

    return render(request, 'contact/contact_form.html', {'form': form})

# contact end

# review start
def add_review(request, consumer_id):
    consumer = get_object_or_404(Consumer, id=consumer_id)
    consumer_name = consumer.name

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Assuming you have a Review model with fields 'comment' and 'rating'
            review = form.save(commit=False)
            review.consumer = consumer
            review.save()
            # You may want to add a success message here
            return redirect('dashboard')  # Redirect to the dashboard or any other page
    else:
        form = ReviewForm()

    return render(request, 'review/review.html', {'consumer_id': consumer_id, 'consumer_name': consumer_name, 'form': form})
# review end

# views.py


def view_reviews(request, consumer_id):
    consumer = get_object_or_404(Consumer, id=consumer_id)
    reviews = Review.objects.filter(consumer=consumer)

    return render(request, 'review/view_reviews.html', {'consumer': consumer, 'reviews': reviews})

#notification

@login_required
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notification/user_notifications.html', {'notifications': notifications})


import smtplib
from email.message import EmailMessage

from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages

@login_required
def send_email(request):
    if request.method == 'POST':
        receiver = request.POST.get('receiver')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[receiver],
        )
        try:
            email.send()
            messages.success(request, 'Email sent successfully!')
        except:
            messages.error(request, 'Failed to send email.')

        return redirect('send_email')

    return render(request, 'email/sendemail.html')


@login_required
def chat(request):
    return render(request, '')

from django.shortcuts import render
from .models import HotelReview
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pandas as pd

def detect_fake_reviews(request):
    # Retrieve all hotel reviews from the database
    reviews = HotelReview.objects.all()

    # Create a dataframe to hold the reviews and labels
    review_data = pd.DataFrame(list(reviews.values('review_text', 'is_fake')))

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(review_data['review_text'], review_data['is_fake'], test_size=0.2, random_state=42)

    # Vectorize the review texts using TF-IDF
    vectorizer = TfidfVectorizer(max_features=1000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train a logistic regression model
    model = LogisticRegression()
    model.fit(X_train_vec, y_train)

    # Predict labels for the test set
    y_pred = model.predict(X_test_vec)

    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)

    return render(request, 'prediction/fake_review.html', {'accuracy': accuracy})


@login_required
def prediction(request):
    # Retrieve all hotel reviews from the database
    reviews = HotelReview.objects.all()

    # Initialize variables to count suspicious reviews and total reviews
    suspicious_reviews_count = 0
    total_reviews_count = 0

    # Loop through each review
    for review in reviews:
        total_reviews_count += 1
        review_text = review.review_text.lower()

        # Check for common indicators of fake reviews
        if "fake" in review_text or "fraud" in review_text or "scam" in review_text:
            suspicious_reviews_count += 1

    # Calculate the percentage of suspicious reviews
    if total_reviews_count > 0:
        percentage_suspicious_reviews = (suspicious_reviews_count / total_reviews_count) * 100
    else:
        percentage_suspicious_reviews = 0

    return render(request, 'prediction/fake_review.html', {'percentage_suspicious_reviews': percentage_suspicious_reviews})


def analyze_comments(request):
    # Retrieve all hotel reviews from the database
    reviews = HotelReview.objects.all()

    # Initialize variables
    total_reviews = reviews.count()
    total_fake_reviews = reviews.filter(is_fake=True).count()
    total_ratings = sum(review.rating for review in reviews)
    average_rating = total_ratings / total_reviews if total_reviews > 0 else 0

    return render(request, 'prediction/analyze_comments.html', {
        'total_reviews': total_reviews,
        'total_fake_reviews': total_fake_reviews,
        'average_rating': average_rating
    })


def display_hotels(request):
    # Retrieve all hotels from the database
    hotels = Hotel.objects.all()

    return render(request, 'prediction/display_hotels.html', {'hotels': hotels})

def  display_HotelReview(request):
    # Retrieve all hotels from the database
    hotels = HotelReview.objects.all()

    return render(request, 'prediction/display_HotelReview.html', {'hotels': hotels})


def analyze_review(comment):
    # Modify the existing lists of keywords with additional fake comment indicators
    review_comments = ['nice', 'excellent', 'wonderful', 'amazing', 'fantastic', 'beautiful', 'good', 'lovely', 'great stay']
    
    # Check for various types of comments
    review_comments_values = any(word in comment.lower() for word in review_comments)
    
    # Determine the type of comment
    if review_comments_values:
        return False  # Fake review
    else:
        return True  # Genuine review


def analyze_review_view(request):
    if request.method == 'POST':
        reviewer_name = request.POST.get('reviewer_name')
        review_text = request.POST.get('review_text')
        rating = request.POST.get('rating')
        hotel_name = request.POST.get('hotel_name')  # Add hotel name extraction

        # Analyze the review text
        is_fake = analyze_review(review_text)

        # Save the review and analysis in the database
        review = HotelReviewFine.objects.create(
            reviewer_name=reviewer_name,
            review_text=review_text,
            rating=rating,
            is_fake=is_fake,
            hotel_name=hotel_name  # Include hotel name when creating the review
        )

        return render(request, 'prediction/review_analysis.html', {'review': review})
    else:
        return render(request, 'prediction/input_form.html')


from django.shortcuts import render
from .models import HotelReviewFine

def display_reviews(request):
    reviews = HotelReviewFine.objects.all()
    return render(request, 'prediction/view.html', {'reviews': reviews})
