from django.shortcuts import render


def index(request):
    template = 'src/pages/main/index.js'
    return render(request, template)
     