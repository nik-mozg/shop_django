# shop/views_auth.py
import json
import logging  # noqa: F401

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def post_sign_in(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            username = data.get("username")
            password = data.get("password")

        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if not username or not password:
            print("Error: Missing username or password")
            return JsonResponse(
                {"error": "Username and password are required"}, status=400
            )

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("User authenticated:", user.username)
            return JsonResponse({"message": "Login successful"}, status=200)
        else:
            print("Error: Invalid username or password")
            return JsonResponse({"error": "Invalid username or password"}, status=401)
    else:
        print("Error: Invalid HTTP method")
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@csrf_exempt
def post_sign_out(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({"message": "Logout successful"}, status=200)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@csrf_exempt
def post_sign_up(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            username = data.get("username")
            password = data.get("password")
            if not name or not username or not password:
                return JsonResponse({"error": "All fields are required"}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already taken"}, status=400)
            user = User.objects.create_user(
                username=username, password=password, first_name=name
            )
            user.save()

            return JsonResponse({"message": "User created successfully"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)
