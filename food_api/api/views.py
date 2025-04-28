from rest_framework import generics
from .models import FoodDrinkItem
from .serializers import FoodDrinkItemSerializer


# Create your views here.
class FoodDrinkListCreate(generics.ListCreateAPIView):
    queryset = FoodDrinkItem.objects.all()
    serializer_class = FoodDrinkItemSerializer


class FoodDrinkRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = FoodDrinkItem.objects.all()
    serializer_class = FoodDrinkItemSerializer
    lookup_field = "pk"