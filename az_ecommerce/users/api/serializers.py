import jwt
import phonenumbers
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.mail import send_mail
from django.template.loader import render_to_string
from jwt.exceptions import ExpiredSignatureError
from jwt.exceptions import InvalidTokenError
from rest_framework import serializers

from az_ecommerce.users.models import User
from az_ecommerce.users.utils import generate_email_token


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["name", "email", "phone"]

    def validate_phone(self, value):
        try:
            phonenumbers.parse(value)
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise serializers.ValidationError(
                {"phone": "Invalid Phone Number format"},
            ) from e
        return value


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "phone", "email", "password", "is_verified"]
        extra_kwargs = {
            "password": {
                "write_only": True,
            },
        }
        read_only_fields = ["is_verified"]

    def validate_phone(self, value):
        try:
            phonenumbers.parse(value)
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise serializers.ValidationError(
                {"phone": "Invalid Phone Number format"},
            ) from e
        return value
    
    def validate(self, attrs):
        user = User(**attrs)
        password = attrs["password"]

        try:
            validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)}) from e

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            **validated_data,
        )
        token = generate_email_token(user)
        verification_url = f"{settings.FRONTEND_URL}/api/verify-email/{token}/"
        email_context = {"user": user, "verification_url": verification_url}

        message = render_to_string("emails/verify_email.html", email_context)
        send_mail(
            subject="Verify Your Email",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return user


class ChangePassSerializer(serializers.Serializer):
    old_pass = serializers.CharField(max_length=255, required=True)
    new_pass = serializers.CharField(max_length=255, required=True)
    old_pass_error = "Old password is not correct."  # noqa: S105

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context.get("request").user

    def validate_old_pass(self, value):
        if not self.user.check_password(value):
            raise serializers.ValidationError({"error": self.old_pass_error})
        return value

    def validate(self, attrs):
        try:
            validate_password(password=attrs["new_pass"], user=self.user)
        except exceptions.ValidationError as e:
            serializers.ValidationError({"new_pass": list(e.messages)})
        return attrs

    def save(self, **kwargs):
        new_pass = self.validated_data.get("new_pass")
        self.user.set_password(new_pass)
        self.user.save()
        return self.user


class RestPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)
    email_error = "No user found with this email."

    def validate(self, attrs):
        self.email = attrs["email"]
        self.user = get_user_model().objects.filter(email=self.email).first()

        if not self.user:
            raise serializers.ValidationError({"error": self.email_error})
        return attrs

    def save(self, **kwargs):
        user = self.user
        token = generate_email_token(user)
        reset_url = f"{settings.FRONTEND_URL}/api/auth/reset-password/{token}/"
        email_context = {
            "user": self.user,
            "reset_url": reset_url,
        }
        email_message = render_to_string("emails/reset_password.html", email_context)
        send_mail(
            subject="Reset Your Password",
            message=email_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get("token")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithm="HS256")
            user = User.objects.get(id=payload["user_id"])
            if user.is_verified:
                raise serializers.ValidationError(
                    {"message": "Email is already verified"},
                )
            attrs["user"] = user
        except ExpiredSignatureError as err:
            raise serializers.ValidationError(
                {"message": "Verification link has expired"},
            ) from err
        except InvalidTokenError as err:
            raise serializers.ValidationError({"message": "token is invalid"}) from err
        except user.DoesNotExist as err:
            raise serializers.ValidationError(
                {"message": "user does not exist"},
            ) from err
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.is_verified = True
        user.save()
        return user
