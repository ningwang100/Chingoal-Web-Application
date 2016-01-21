from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.contrib.auth.views import password_reset, password_reset_confirm,password_change_done
import json
import hashlib, random
from django.contrib import messages
from datetime import datetime, timedelta

from models import *
from forms import *
from django.shortcuts import render_to_response, get_object_or_404
from itertools import chain

from mimetypes import guess_type
from drealtime import iShoutClient
ishout_client = iShoutClient()

def reset_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request, template_name='account/reset_confirm.html',
        uidb64=uidb64, token=token, post_reset_redirect=reverse('home'))

def reset(request):
    context={}
    if request.method == 'POST':
        form = request.POST
        data = {
            'form': form,
        }
        value = data['form']
        user_input=value.get("email",0)
        try:
            user = User.objects.get(email = user_input)
        except User.DoesNotExist:
            user = None
        if Learner.objects.filter(user__exact = user) or Teacher.objects.filter(user__exact = user):
            return password_reset(request, template_name='account/reset.html',
            email_template_name='account/reset_email.html',
            subject_template_name='account/reset_subject.txt',
            post_reset_redirect=reverse('login'))
        else:
            context['error'] = "This email address is invalid"
            context['form']=PasswordResetForm()
            return render(request, 'account/reset.html',context)
    return password_reset(request, template_name='account/reset.html',
            email_template_name='account/reset_email.html',
            subject_template_name='account/reset_subject.txt',
            post_reset_redirect=reverse('reset'))


def register(request,flag):

    if flag!='0' and flag!='1':
        return HttpResponseNotFound('<h1>No Page Here</h1>')
    context = {}
    for key in request.POST:
        print key + ":" + request.POST[key]
    if flag == '1':
        context['register_form'] = RegistrationForm()
        context['hint'] = 'The Activation link is invalid, please double check it' 
        context['judge'] = '1'
        context['parameter']='0'
        return render(request, 'account/register.html', context)
    if request.method == 'GET':
        context['register_form'] = RegistrationForm()
        context['judge']='0'
        context['parameter']='0'
        return render(request, 'account/register.html', context)
    
    register_form = RegistrationForm(request.POST)
    context['register_form'] = register_form
    if not register_form.is_valid():
        return render(request, 'account/register.html', context)
    register_form.save()
    username=register_form.cleaned_data['username']
    email=register_form.cleaned_data['email']
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    activation_key = hashlib.sha1(salt+email).hexdigest()
    new_user=User.objects.get(username=username)
    if request.POST['optionsRadiosInline'] == 'option1':
        identity = 0
    elif request.POST['optionsRadiosInline'] == 'option2':
        identity = 1

    if identity == 0:
        new_learner = Learner.objects.create(user=new_user,activation_key=activation_key)
        new_learner.save()

    elif identity == 1:
        new_teacher = Teacher.objects.create(user=new_user,activation_key=activation_key)
        new_teacher.save()
    email_subject = 'Account confirmation'
    email_body = "Hey %s, thanks for signing up. To activate your account, click this link\
                http://chingoal.us//account/confirm/%s" % (register_form.cleaned_data['username'], activation_key)
            
    send_mail(email_subject, email_body, '15637test@gmail.com', [register_form.cleaned_data['email']], fail_silently=False)
    messages.add_message(request, messages.INFO, 'A confirmation email has been sent to your email address.')
    context['parameter']='0'
    return render(request, 'account/register.html', context)

def login_user(request):
    username = password = ''
    context = {}
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/home')
            else:
                context = {}
                context['error'] = "User is not activated"
                context['parameter']='0'
                return render(request,'account/login.html',context)
        context={}
        context['error'] = "Wrong username or password"
        context['parameter']='0'
        return render(request,'account/login.html',context)
    context['parameter']='0'
    return render(request,'account/login.html',context)

def fb_login(request):
    name = request.POST['username'].replace(" ","")
    if len(User.objects.filter(username = name)) > 0:
	    print "old user"
	    old_user = authenticate(username=name, \
                            password=request.POST['defaultPassword'])
        #print "username:" + request.POST['username']
	    login(request, old_user)
    else:
        print "new user"
        # Creates the new user from the valid form data
        print "username:" + name
        new_user = User.objects.create_user(username=name, \
                                        password=request.POST['defaultPassword'])
        new_user.save()
        new_learner = Learner.objects.create(user=new_user,activation_key="123")
        new_learner.save()
        # Logs in the new user and redirects to his/her todo list
        new_user = authenticate(username=name, \
                            password=request.POST['defaultPassword'])
        login(request, new_user)
    print 'login success'
    return HttpResponse("")

@login_required
def edit_profile(request):
    if Learner.objects.filter(user = request.user):
        flag = 0
    else:
        flag = 1
    if request.method == 'GET':
        return render(request, 'account/edit_profile.html', {'editForm': EditProfileForm(),'username':request.user.username,'flag':flag})

    edit_form = EditProfileForm(request.POST, request.FILES)
    errors = []
    if not request.user.check_password(request.POST['password1']):
        errors.append('Old password is incorrect.')
    
    if errors:
        return render(request, 'account/edit_profile.html', {'errors':errors, 'msg':'no','editForm': edit_form,'username':request.user.username,'flag':flag})

    if not edit_form.is_valid():
        return render(request, 'account/edit_profile.html',{'editForm': edit_form, 'msg':'no','username':request.user.username,'flag':flag})
    
    if edit_form.cleaned_data['password2']:
        request.user.set_password(edit_form.cleaned_data['password2'])

    if edit_form.cleaned_data['photo']:
        new_photo = edit_form.cleaned_data['photo']
        if Learner.objects.filter(user = request.user):
            request.user.learner_user.photo = new_photo
        elif Teacher.objects.filter(user = request.user):
            request.user.teacher.photo = new_photo

    if edit_form.cleaned_data['bio']:
        new_bio = edit_form.cleaned_data['bio']
        if Learner.objects.filter(user = request.user):
            request.user.learner_user.bio = new_bio
        elif Teacher.objects.filter(user = request.user):
            request.user.teacher.bio = new_bio

    request.user.save()
    if Learner.objects.filter(user = request.user):
        request.user.learner_user.save()
    elif Teacher.objects.filter(user = request.user):
        request.user.teacher.save()
    return render(request, 'account/edit_profile.html', {'errors':errors, 'msg':'yes','editForm': EditProfileForm(),'username':request.user.username,'flag':flag})

@login_required
def view_profile(request, uname):
    if not User.objects.filter(username__exact = uname):
        return HttpResponseNotFound('<h1>No User</h1>')
    context = {}
    if request.user.newmsg.filter(isReply=True).count() > 10:
        request.user.newmsg.filter(isReply=True).delete()
    if request.user.newmsg.filter(isReply=False):
        context['hasnewmsg'] = 'yes'
    else:
        context['hasnewmsg'] = 'no'
    cur_user = User.objects.get(username__exact = uname)
    context['username'] = uname
    context['uid'] = cur_user.id
    context['cur_username'] = request.user.username

    context['cur_uid'] = request.user.id
    context['newmsgs'] = request.user.newmsg.all().order_by('-timestamp')
    context['msgcount'] = request.user.newmsg.all().count()

    if History.objects.filter(user__exact = cur_user):
        context['historys'] = History.objects.filter(user__exact = cur_user).order_by('-timestamp')
        last1hour = datetime.today() - timedelta(hours = 1)
        last2hour = datetime.today() - timedelta(hours = 2)
        last3hour = datetime.today() - timedelta(hours = 3)
        last4hour = datetime.today() - timedelta(hours = 4)
        last5hour = datetime.today() - timedelta(hours = 5)
        last6hour = datetime.today() - timedelta(hours = 6)
        count1 = History.objects.filter(user__exact = cur_user, kind='learn',timestamp__gt=last1hour).count()
        count2 = History.objects.filter(user__exact = cur_user, kind='learn',timestamp__gt=last2hour, timestamp__lt=last1hour).count()
        count3 = History.objects.filter(user__exact = cur_user, kind='learn',timestamp__gt=last3hour, timestamp__lt=last2hour).count()
        count4 = History.objects.filter(user__exact = cur_user, kind='learn',timestamp__gt=last4hour, timestamp__lt=last3hour).count()
        count5 = History.objects.filter(user__exact = cur_user, kind='learn',timestamp__gt=last5hour, timestamp__lt=last4hour).count()
        count6 = History.objects.filter(user__exact = cur_user, kind='learn',timestamp__gt=last6hour, timestamp__lt=last5hour).count()
        points = {}
        points['1']=105-8*count1
        points['2']=105-8*count2
        points['3']=105-8*count3
        points['4']=105-8*count4
        points['5']=105-8*count5
        points['6']=105-8*count6
        context['points'] = points

    if Learner.objects.filter(user__exact = request.user):
        
        request_user_learner = Learner.objects.get(user__exact = request.user)
        if request_user_learner.follows.filter(username__exact = cur_user.username):
            context['isFollowing'] = 'yes'
        else:
            context['isFollowing'] = 'no'
        context['scheduleForm'] = EditScheduleForm(initial={'progress_level':request_user_learner.progress_level,'progress_lesson':request_user_learner.progress_lesson})

    else:
        
        request_user_teacher = Teacher.objects.get(user__exact = request.user)
        print request_user_teacher
        if request_user_teacher.follows.filter(username__exact = cur_user.username):
            context['isFollowing'] = 'yes'
        else:
            context['isFollowing'] = 'no'


    if Learner.objects.filter(user = cur_user):
        cur_user_learner = Learner.objects.get(user__exact = cur_user)
        follow_users = cur_user_learner.follows.all()
        context['cur_user'] = cur_user_learner
        context['isLearner'] = 'yes'
    else:
        cur_user_teacher = Teacher.objects.get(user__exact = cur_user)
        follow_users = cur_user_teacher.follows.all()
        context['cur_user'] = cur_user_teacher
        context['isLearner'] = 'no'

    followers_learner = Learner.objects.none()
    followers_teacher = Teacher.objects.none()
    unfollowers_learner = Learner.objects.none()
    unfollowers_teacher = Teacher.objects.none()

    unfollowers_learner = Learner.objects.exclude(user__in=follow_users)
    if unfollowers_learner.filter(user__exact = cur_user):
        unfollowers_learner = unfollowers_learner.exclude(user__exact = cur_user)

    unfollowers_teacher = Teacher.objects.exclude(user__in=follow_users)
    if unfollowers_teacher.filter(user__exact = cur_user):
        unfollowers_teacher = unfollowers_teacher.exclude(user__exact = cur_user)

    if Learner.objects.filter(user__in=follow_users):
        followers_learner = Learner.objects.filter(user__in=follow_users)


    if Teacher.objects.filter(user__in=follow_users):
        followers_teacher = Teacher.objects.filter(user__in=follow_users)

    followers = list(chain(followers_learner,followers_teacher))
    unfollowers = list(chain(unfollowers_learner,unfollowers_teacher))

    context['followers'] = followers
    context['unfollowers'] = unfollowers
    return render(request, 'account/view_profile.html', context)

def reset_password(request):
    context = {}
    return render(request, 'resetPassword.html', context)

def new_password(request,token):
    return redirect('/')

@login_required
def edit_schedule(request):
    if request.method == 'GET':
        return HttpResponse("Please add something by POST method.")

    scheduleForm = EditScheduleForm(request.POST)

    if scheduleForm.is_valid():
        pass

    if scheduleForm.cleaned_data['progress_level']:
        progress_level = scheduleForm.cleaned_data['progress_level']
        request.user.learner_user.progress_level = progress_level

    if scheduleForm.cleaned_data['progress_lesson']:
        progress_lesson = scheduleForm.cleaned_data['progress_lesson']
        request.user.learner_user.progress_lesson = progress_lesson
    request.user.learner_user.save()
    return redirect(reverse('viewProfile', kwargs = {'uname':request.user.username}))

@login_required
def follow(request, uname, isFollowing, isLearner):
    followee = User.objects.get(username__exact = uname)
    if Learner.objects.filter(user__exact = request.user):
        follower = request.user.learner_user
    else:
        follower = request.user.teacher
        print "is teacher"

    if isFollowing == 'yes':
        if follower.follows.filter(username__exact = followee.username):
            follower.follows.remove(followee)
            follower.save()
    else:
        print "follow function: is following no"
        print follower.follows.filter(username__exact = followee.username)
        if not follower.follows.filter(username__exact = followee.username):
            follower.follows.add(followee)
            follower.save()

    return redirect(reverse('viewProfile', kwargs = {'uname':uname}))

@login_required
def post_question(request):
    errors = None
    if not 'text' in request.POST or not request.POST['text']:
        errors = 'You must enter something.'
    else:
        if len(request.POST['text']) > 42:
            errors = 'You post message need to 42 characters or less.'
            context = {'posts': Grumblr.objects.all().order_by('-time')}
            context['add_post_errors'] = errors
            return render(request, 'grumblr/global_stream.html', context)
        else:
            new_post = Grumblr(user=request.user, content=request.POST['text'])
            new_post.save()
    newUser = UserProfile.objects.get(user=request.user)
    context = {'posts': Grumblr.objects.all().order_by('-time')}
    context['add_post_errors'] = errors
    context['newUser'] = newUser
    return render(request, 'grumblr/global_stream.html', context)

def register_confirm(request, activation_key):
    #check if user is already logged in and if he is redirect him to some other url, e.g. home
    if request.user.is_authenticated():
        HttpResponseRedirect('/home')
    
    # check if there is UserProfile which matches the activation key (if not then display 404)
    if Teacher.objects.filter(activation_key=activation_key):
        new_user = Teacher.objects.get(activation_key__exact=activation_key)
    elif Learner.objects.filter(activation_key=activation_key):
        new_user = Learner.objects.get(activation_key__exact=activation_key)
    else:
        flag = '1'
        return register(request,flag)
    #if the key hasn't expired save user and set him as active and render some template to confirm activation
    user = new_user.user
    user.is_active = True
    user.save()
    return redirect(reverse('login'))


@login_required
def get_photo(request, username):

    user_temp = Learner.objects.filter(user__username = username)
    is_learner = len(user_temp)
    if is_learner == 1:
        cur_user = user_temp[0]
    else:
        cur_user = Teacher.objects.get(user__username = username)    
        
    if not cur_user.photo:
        raise Http404

    content_type = guess_type(cur_user.photo.name)

    return HttpResponse(cur_user.photo, content_type = content_type)

@login_required
def send(request,receiver_name, sender_name):
    text = request.POST['textarea1']
    sender = request.user.username
    if len(text) > 0:
        receiver = User.objects.get(username__exact = receiver_name)
        newmsg = Newmsg(user=receiver, text=text, sender=sender)
        newmsg.save()
        count = receiver.newmsg.all().count()
        ishout_client.emit(
            receiver.id,
            'alertchannel',
            data = {'count':count,'time':str(datetime.now()), 'text':text, 'sender':sender, 'receiver':sender_name, 'msgid':newmsg.id}
        )
    return redirect(reverse('viewProfile', kwargs = {'uname':sender_name}))


@login_required
def reply(request,receiver_name, sender_name, replyid):
    tmp = request.user.newmsg.get(id__exact = replyid)
    tmp.isReply = True
    tmp.save()
    text = request.POST['textarea1']
    sender = request.user.username
    if len(text) > 0:
        receiver = User.objects.get(username__exact = receiver_name)
        newmsg = Newmsg(user=receiver, text=text, sender=sender)
        newmsg.save()
        count = receiver.newmsg.all().count()
        ishout_client.emit(
                           int(receiver.id),
                           'alertchannel',
                           data = {'count':count,'time':str(datetime.now()), 'text':text, 'sender':sender, 'receiver':sender_name, 'msgid':newmsg.id}
                           )
    return redirect(reverse('viewProfile', kwargs = {'uname':sender_name}))

@login_required
def dismiss(request, replyid):
    tmp = request.user.newmsg.get(id__exact = replyid)
    tmp.isReply = True
    tmp.save()
    return redirect(reverse('viewProfile', kwargs = {'uname':request.user.username}))






