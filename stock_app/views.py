from django.shortcuts import render

def home(request):
    return render(request, 'stock_app/home.html', {})