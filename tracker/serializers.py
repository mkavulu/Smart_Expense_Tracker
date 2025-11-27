from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Transaction, Category, Budget


# ---------------------------------------------------------
# User Registration Serializer (with password confirmation)
# ---------------------------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2", "first_name", "last_name")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )


# ---------------------------------------------------------
# Category Serializer
# ---------------------------------------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "type")
        read_only_fields = ("id",)

    def validate(self, data):
        user = self.context["request"].user

        if Category.objects.filter(
            user=user,
            name__iexact=data["name"],
            type=data["type"],
        ).exists():
            raise serializers.ValidationError("Category already exists.")

        return data


# ---------------------------------------------------------
# Transaction Serializer
# ---------------------------------------------------------
class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_type = serializers.CharField(source="category.type", read_only=True)
    receipt = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ("id", "user", "category_name", "category_type")

    def get_receipt(self, obj):
        request = self.context.get("request")
        if obj.receipt and request:
            return request.build_absolute_uri(obj.receipt.url)
        elif obj.receipt:
            return obj.receipt.url
        return None

    def validate(self, data):
        if data["amount"] <= 0:
            raise serializers.ValidationError("Amount must be positive.")

        if data.get("category") and data["category"].type != data["type"]:
            raise serializers.ValidationError("Transaction type must match category type.")

        return data

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


# ---------------------------------------------------------
# Budget Serializer
# ---------------------------------------------------------
class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Budget
        fields = "__all__"
        read_only_fields = ("id",)
