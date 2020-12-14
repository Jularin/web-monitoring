from django.db import models


class DateTimeFieldWithoutTimeZone(models.DateTimeField):
    def db_type(self, connection):
        return 'timestamp'


class Url(models.Model):
    url = models.URLField(null=False)
# TODO  Object of type datetime is not JSON serializable
    last_check_time = DateTimeFieldWithoutTimeZone(auto_now=True, null=True)
    status_code = models.IntegerField(null=True)
    status = models.CharField(max_length=10, null=True)
    error = models.CharField(max_length=100, null=True)
    final_url = models.URLField(null=True)

    def __str__(self):
        return self.url


