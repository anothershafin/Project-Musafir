from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class SignupSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('psg', 'Passenger'), ('drv', 'Driver')], write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone', 'role']

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        UserProfile.objects.create(user=user, phone=phone, role=role)
        return user
    
#2fa
class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()