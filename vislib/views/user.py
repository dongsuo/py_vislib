import json
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@csrf_exempt
def userInfo(request):
    if request.user.is_authenticated:
        username = request.user.get_username()
        return JsonResponse({'code': 20000, 'data': {'username': username}})
    else:
        return JsonResponse({'code': 40000, 'message': 'Please login'})

@csrf_exempt
def userSignup(request):
    body = json.loads(request.body)
    if User.objects.filter(username=body['userName']).exists():
        return JsonResponse({'code': 10000, 'message': 'User Name ' +  body['userName'] + ' is Already Tabken.'})
    if User.objects.filter(email=body['email']).exists():
        return JsonResponse({'code': 10000, 'message': 'Email ' +  body['emaul'] + ' is Registered.'})
    user = User.objects.create_user(body['userName'], body['email'], body['password'])
    user.first_name=body['userName']
    user.save()
    return JsonResponse({'code': 20000, 'message': 'success'})

@csrf_exempt
def userLogin(request):
    body = json.loads(request.body)
    user = authenticate(request, username=body['userName'], password=body['password'])
    if user is not None:
        login(request, user)
        return JsonResponse({'code': 20000, 'message': 'success'})
    else:
        return JsonResponse({'code': 10000, 'message': 'Name or Password Not Correct, Please Try Again.'})

@csrf_exempt
def userLogout(request):
    logout(request)
    return JsonResponse({'code': 20000, 'message': 'success'})
