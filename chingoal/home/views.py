from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse

import json

from account.models import *
from account.forms import *

# Create your views here.
def homepage(request):
    context = {}
    context['username'] = request.user.username
    context['parameter']='0'
    return render(request, 'home.html', context)

@login_required
def home(request):
    context = {}
    cur_user = request.user
    context['username'] = cur_user.username
    context['newmsgs'] = request.user.newmsg.all().order_by('-timestamp')
    context['msgcount'] = request.user.newmsg.all().count()
    if Learner.objects.filter(user = request.user):
        learner = Learner.objects.get(user = cur_user)
        context['cur_user'] = learner
        context['flag'] = 0
    
    if Teacher.objects.filter(user = request.user):
        teacher = Teacher.objects.get(user = cur_user)
        context['cur_user'] = teacher
        context['flag'] = 1
    if request.user.newmsg.filter(isReply=False):
        context['hasnewmsg'] = 'yes'
    else:
        context['hasnewmsg'] = 'no'
    return render(request, 'dashboard.html', context)