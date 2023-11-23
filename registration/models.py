from django.db import models
from django.db import models
from django.contrib.auth.models import User


class Userreg(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User')
    title = models.CharField(max_length=5)
    domain = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username
