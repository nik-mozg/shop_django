# shop/views_profile.py.py
import json
import logging  # noqa: F401

from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse

from .models import Profile
from .serializers import ProfileSerializer

# logger = logging.getLogger('custom_logger')


def profile_view(request):
    if request.method == "GET":
        return get_profile(request)
    elif request.method == "POST":
        return post_profile(request)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def get_profile(request):
    if request.user.is_authenticated:
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
            if created:
                print(f"Profile created for user: {request.user.username}")

            serializer = ProfileSerializer(profile, context={"request": request})
            serialized_data = serializer.data
            return JsonResponse(serialized_data)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse(
                {"error": "An error occurred while fetching the profile"}, status=500
            )
    else:
        print("Error: User not authenticated")
        return JsonResponse({"error": "User not authenticated"}, status=401)


def post_profile_avatar(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        if "avatar" not in request.FILES:
            return JsonResponse({"error": "No avatar file provided"}, status=400)

        avatar = request.FILES["avatar"]
        avatar_error = validate_avatar(avatar)
        if avatar_error:
            return JsonResponse({"error": avatar_error}, status=400)

        try:
            profile = request.user.profile
            profile.avatar = avatar
            profile.save()

            return JsonResponse({"message": "Avatar updated successfully"}, status=200)
        except Profile.DoesNotExist:
            return JsonResponse({"error": "Profile not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def post_profile(request):
    if request.method == "POST":
        try:
            print("Request body:", request.body)
            data = json.loads(request.body)
            print("Parsed data:", data)

            fullName = data.get("fullName", "").strip()
            email = data.get("email", "").strip()
            phone = data.get("phone", "").strip()
            errors = {}

            # Валидация данных
            if not fullName:
                errors["fullName"] = "Full name is required"
            email_error = validate_email_field(email)
            if email_error:
                errors["email"] = email_error
            phone_error = validate_phone(phone)
            if phone_error:
                errors["phone"] = phone_error
            unique_errors = check_unique_fields(phone, email, request.user)
            if unique_errors:
                errors.update(unique_errors)
            if errors:
                print("Validation errors:", errors)
                return JsonResponse({"errors": errors}, status=400)
            profile, created = Profile.objects.get_or_create(
                user=request.user,
                defaults={
                    "fullName": fullName,
                    "email": email,
                    "phone": phone,
                },
            )
            if not created:
                profile.fullName = fullName
                profile.email = email
                profile.phone = phone
                profile.save()

            return JsonResponse({"message": "Profile updated successfully"}, status=200)

        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def post_profile_password(request):
    if request.method == "POST":
        print("Смена пароля ")
        try:
            data = json.loads(request.body)
            current_password = data.get("currentPassword")
            print("current Password: ", current_password)
            new_password = data.get("newPassword")
            print("new_password ", new_password)

            if not current_password or not new_password:
                return JsonResponse(
                    {"error": "Both current and new passwords are required"}, status=400
                )
            if not request.user.is_authenticated:
                return JsonResponse({"error": "User not authenticated"}, status=401)
            if not check_password(current_password, request.user.password):
                return JsonResponse(
                    {"error": "Current password is incorrect"}, status=400
                )
            if current_password == new_password:
                return JsonResponse(
                    {
                        "error": "New password cannot be the same as the current password"
                    },
                    status=400,
                )
            request.user.set_password(new_password)
            request.user.save()
            login(request, request.user)

            return JsonResponse(
                {"message": "Password updated successfully"}, status=200
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def validate_phone(phone):
    """
    Проверяет, что телефон начинается с +7 или 8 и состоит из 11 цифр.
    """
    if not phone:
        return "Phone number is required"
    phone = phone.replace(" ", "").replace("-", "").strip()
    if phone.startswith("+7"):
        normalized_phone = phone[2:]
    elif phone.startswith("8"):
        normalized_phone = phone[1:]
    else:
        return "Phone number must start with +7 or 8"
    if not normalized_phone.isdigit() or len(normalized_phone) != 10:
        return "Phone number must contain 11 digits (including +7 or 8)"

    return None


def validate_email_field(email):
    """
    Проверяет корректность email.
    """
    if not email:
        return "Email is required"
    try:
        validate_email(email)
    except ValidationError:
        return "Invalid email format"
    return None


def check_unique_fields(phone, email, user):
    """
    Проверяет уникальность телефона и email.
    """
    from .models import Profile

    if Profile.objects.filter(phone=phone).exclude(user=user).exists():
        return {"phone": "Phone number is already in use"}
    if Profile.objects.filter(email=email).exclude(user=user).exists():
        return {"email": "Email is already in use"}
    return None


def validate_avatar(file):
    """
    Проверяет, что файл является изображением и размером не более 2 МБ.
    """
    if not file.content_type.startswith("image/"):
        return "File must be an image"
    if file.size > 2 * 1024 * 1024:
        return "Image size must not exceed 2 MB"
    return None
