from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category


def index(request):
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    context_dict = {
        'boldmessage': "This tutorial has been put together by Simon."}
    return render(request, 'rango/about.html', context=context_dict)

