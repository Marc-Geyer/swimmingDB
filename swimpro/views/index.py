from django.shortcuts import render


def index(request):
    return render(request, 'index.html')

def websocket_test(request):
    return render(request, 'websocket_test.html')