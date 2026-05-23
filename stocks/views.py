from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import date, timedelta
import json
import threading

from .models import Stock, StockHistory, ContactMessage, Subscriber
from django.core.paginator import Paginator

# Home page
def home(request):
    return render(request, "home.html")

@login_required(login_url='/login/')
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    is_admin = request.user.is_staff
    user_role = "Admin" if is_admin else "Employee"

    try:
        symbol = request.GET.get('symbol', '').strip()
        if symbol:
            stock_list = Stock.objects.filter(symbol__icontains=symbol)
        else:
            stock_list = Stock.objects.all()

        paginator = Paginator(stock_list, 10)  # 10 stocks per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        stocks = page_obj

        chart_labels = [s.symbol for s in stocks]
        chart_data = [s.price for s in stocks]

        for stock in stocks:
            history = list(stock.stockhistory_set.order_by('date'))
            if history:
                labels = [h.date.strftime('%b %d') for h in history]
                candlesticks = []
                for h in history:
                    close = float(h.price)
                    open_price = close * 0.995
                    high = close * 1.01
                    low = close * 0.99
                    candlesticks.append({
                        "o": round(open_price, 2),
                        "h": round(high, 2),
                        "l": round(low, 2),
                        "c": round(close, 2)
                    })
            else:
                labels = [
                    (date.today() - timedelta(days=i)).strftime('%b %d')
                    for i in range(4, -1, -1)
                ]
                candlesticks = []
                base_price = float(stock.price or 0)
                for idx, _label in enumerate(labels):
                    close = base_price * (1 + (idx - 2) * 0.01)
                    open_price = close * 0.99
                    high = close * 1.013
                    low = close * 0.987
                    candlesticks.append({
                        "o": round(open_price, 2),
                        "h": round(high, 2),
                        "l": round(low, 2),
                        "c": round(close, 2)
                    })

            stock.candlestick_labels = json.dumps(labels)
            stock.candlestick_data = json.dumps(candlesticks)

        return render(request, "stocks/dashboard.html", {
            "stocks": stocks,
            "page_obj": page_obj,
            "chart_labels": chart_labels,
            "chart_data": chart_data,
            "is_admin": is_admin,
            "user_role": user_role,
            "total_companies": Stock.objects.count(),
            "total_messages": ContactMessage.objects.count(),
            "top_gainer": "RELIANCE +3.5%",
            "top_loser": "TITAN -2.1%",
            "market_status": "Open",
        })
    except Exception as e:
        messages.error(request, f"Error loading dashboard: {e}")
        return redirect("home")


# Async mail sender
def send_email_async(subject, body, to_email):
    send_mail(subject, body, settings.EMAIL_HOST_USER, [to_email])


# Contact form
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        ContactMessage.objects.create(name=name, email=email, message=message)
        subject = f"New Contact Form Submission from {name}"
        body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
        threading.Thread(target=send_email_async, args=(subject, body, settings.EMAIL_HOST_USER)).start()
        messages.success(request, "Message sent!")
        return redirect("contact")
    return render(request, "contact.html")


# Subscriber form
def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            if Subscriber.objects.filter(email=email).exists():
                messages.warning(request, "You are already subscribed!")
            else:
                Subscriber.objects.create(email=email)
                messages.success(request, "Thanks for subscribing!")

                # Notification mail to Admin
                subject_admin = f"New Subscriber: {email}"
                body_admin = f"A new user has subscribed with email: {email}"
                threading.Thread(
                    target=send_email_async,
                    args=(subject_admin, body_admin, settings.EMAIL_HOST_USER)
                ).start()

                # Auto-reply mail to Subscriber
                subject_user = "Subscription Successful - Titan Trade"
                body_user = (
                    f"Hello,\n\n"
                    f"Thank you for subscribing to Titan Trade updates!\n"
                    f"We’ll keep you informed with the latest news and insights.\n\n"
                    f"Regards,\nTitan Trade Team"
                )
                threading.Thread(
                    target=send_email_async,
                    args=(subject_user, body_user, email)
                ).start()

        return redirect("home")


# Custom login
def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {username}, you have successfully logged in!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")


# Custom register
def custom_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        admin_code = request.POST.get("admin_code", "").strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
        elif password != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another one.")
        elif admin_code and admin_code != settings.ADMIN_APPROVAL_CODE:
            messages.error(request, "Invalid admin approval code.")
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email or ""
            )
            user.is_staff = bool(admin_code)
            user.is_superuser = False
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.save()
            login(request, user)
            if user.is_staff:
                messages.success(request, "Admin account created with approval code.")
            else:
                messages.success(request, "Your account has been created and you are now logged in.")
            return redirect("dashboard")
    return render(request, "register.html")


def about(request):
    return render(request, "about.html")


@login_required(login_url='/login/')
def profile(request):
    return render(request, "profile.html", {"user": request.user})


@login_required(login_url='/login/')
def admin_panel(request):
    if not request.user.is_staff:
        messages.error(request, "Admin access only.")
        return redirect("dashboard")

    return render(request, "stocks/admin_panel.html", {
        "total_stocks": Stock.objects.count(),
        "total_messages": ContactMessage.objects.count(),
    })


@login_required(login_url='/login/')
def delete_account(request):
    user = request.user
    username = user.username
    user.delete()
    messages.success(request, f"Account '{username}' deleted successfully.")
    return redirect("home")
