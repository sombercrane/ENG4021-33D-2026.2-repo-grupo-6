from django.shortcuts import render


def iag(request):
    return render(request, "iag.html")


def kennedy(request):
    return render(request, "kennedy.html")

def rdc(request):
    return render(request, "rdc.html")