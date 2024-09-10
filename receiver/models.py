from django.db import models
from django.db.models.signals import post_migrate
from django.contrib.auth.hashers import make_password
import receiver

class UserCredentials(models.Model):
    username = models.CharField(unique=True, max_length=150)
    password = models.CharField(max_length=128)  # Adjust max_length as needed

    def __str__(self):
        return self.username


class RockBlockMessage(models.Model):
    imei = models.CharField(max_length=100)
    momsn = models.IntegerField()
    transmit_time = models.TextField()
    iridium_latitude = models.FloatField()
    iridium_longitude = models.FloatField()
    iridium_cep = models.FloatField()
    data = models.TextField()

    def __str__(self):
        return f"IMEI: {self.imei}, Message Number: {self.momsn}"
    
class RockBlockMessage2(models.Model):
    imei = models.CharField(max_length=100)
    momsn = models.IntegerField()
    transmit_time = models.TextField()
    iridium_latitude = models.FloatField()
    iridium_longitude = models.FloatField()
    iridium_cep = models.FloatField()
    data = models.TextField()
    header = models.TextField()
    doa = models.IntegerField(null=True, blank=True)
    depth = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"IMEI: {self.imei}, Message Number: {self.momsn}"
    
class RockBlockMessageDepth(models.Model):
    imei = models.CharField(max_length=100)
    momsn = models.IntegerField()
    transmit_time = models.TextField()
    iridium_latitude = models.FloatField()
    iridium_longitude = models.FloatField()
    iridium_cep = models.FloatField()
    data = models.TextField()
    header = models.TextField()
    doa = models.IntegerField(null=True, blank=True)
    depth = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"IMEI: {self.imei}, Message Number: {self.momsn}"