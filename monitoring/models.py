from django.db import models


class Url(models.Model):
    url = models.CharField(max_length=100)
    last_check_time = models.CharField(max_length=25)
    status_code = models.IntegerField()
    status = models.CharField(max_length=10, null=True)
    error = models.CharField(max_length=100)
    final_url = models.CharField(max_length=100)

    def __str__(self):
        return self.url
