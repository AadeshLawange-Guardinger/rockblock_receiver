from django.db import models

# Create your models here.

class RockBlockMessage(models.Model):
    imei = models.CharField(max_length=100)
    momsn = models.IntegerField()
    transmit_time = models.DateTimeField()
    iridium_latitude = models.FloatField()
    iridium_longitude = models.FloatField()
    iridium_cep = models.FloatField()
    data = models.TextField()

    def __str__(self):
        return f"IMEI: {self.imei}, Message Number: {self.momsn}"