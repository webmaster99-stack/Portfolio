from django.urls import path
from . import views

urlpatterns = [
    path("foods/", views.FoodDrinkListCreate.as_view()),
    path("foods/<int:id>", views.FoodDrinkRetrieveUpdateDestroy.as_view())
]