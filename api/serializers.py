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



# class ReactAdminCreateSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(
#         write_only=True,
#         min_length=8,
#         trim_whitespace=False
#     )

#     class Meta:
#         model = User
#         fields = ["email", "phone", "name", "password"]

#     def create(self, validated_data):
#         return User.objects.create_user(
#             email=validated_data["email"],
#             phone=validated_data["phone"],
#             name=validated_data["name"],
#             password=validated_data["password"],
#             role=User.REACT_ADMIN,
#         )
