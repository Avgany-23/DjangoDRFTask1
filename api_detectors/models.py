from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Detector(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, default='no description')

    def __str__(self):
        return self.name


class TemporaryMeasurement(models.Model):
    class Meta:
        """Ограничения на уровне БД"""
        constraints = [
            models.CheckConstraint(
                check=models.Q(temporary__lte=100, temporary__gte=-100),
                name='chk_temporary',
            ),
        ]

    temporary = models.FloatField(validators=[MinValueValidator(-100), MaxValueValidator(100)])
    date_time = models.DateTimeField(auto_now_add=True)
    detectors = models.ForeignKey('Detector', on_delete=models.CASCADE, related_name='temp')
