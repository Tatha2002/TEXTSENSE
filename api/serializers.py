from rest_framework import serializers
from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8,trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True,trim_whitespace=False)

    class Meta:
        model = User
        fields = ["email","phone","name","password","confirm_password"]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"Confirm Password": "Passwords do not match."})

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        # Role is fixed by the backend.
        return User.objects.create_user(
            email=validated_data["email"],
            phone=validated_data["phone"],
            name=validated_data["name"],
            password=validated_data["password"],
            role=User.REACT_USER,
        )


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(label="Email/Phone")
    password = serializers.CharField(write_only=True,trim_whitespace=False)



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6, trim_whitespace=False)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_token = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        return attrs