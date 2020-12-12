from django.db import models


class Url(models.Model):
    url = models.URLField(null=False)
    last_check_time = models.DateTimeField(auto_now=True)
    status_code = models.IntegerField(null=True)
    status = models.CharField(max_length=10, null=True)
    error = models.CharField(max_length=100, null=True)
    final_url = models.URLField(null=True)

    def __str__(self):
        return self.url
