from rest_framework import serializers
from .models import FoodDrinkItem


class FoodDrinkItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodDrinkItem
        fields = ["id", "name", "calories", "protein", "carbs", "fat"]
