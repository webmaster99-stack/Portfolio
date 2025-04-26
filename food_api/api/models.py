from django.db import models

# Create your models here.
class FoodDrinkItem(models.Model):
    name = models.CharField(max_length=300)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    objects = models.Manager()

    def __str__(self):
        return self.name