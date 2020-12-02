from json import dumps

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import UrlForm
from .models import Url
from .requests_to_urls import add_new_url_in_db


def index(request):
    urls = Url.objects.all()
    return render(request, 'monitoring/index.html', {'title': 'Main page', 'urls': urls})


def status(request):
    # TODO Django Rest Framework
    result_json = {}
    for row in Url.objects.all():
        result_json[row.url] = {
            'last_check_time': row.last_check_time,
            'status_code': row.status_code,
            'status': row.status,
            'error': row.error,
            'final_url': row.final_url
        }
    return HttpResponse(dumps(result_json), content_type='application/json')


@csrf_exempt  # чтобы Post запрос без csrf token
def add(request):
    if request.method == 'POST':
        form = UrlForm(request.POST)
        add_new_url_in_db(form.data['url'].split())
    form = UrlForm()
    context = {
        'form': form
    }
    return render(request, 'monitoring/urls.html', context)
