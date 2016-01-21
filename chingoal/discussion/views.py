from django.shortcuts import render, redirect, render_to_response

from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, Http404, JsonResponse

from django.db import transaction

from forms import *
from models import *

from account.models import *
import time
import json
from itertools import chain
from drealtime import iShoutClient
ishout_client = iShoutClient()
from datetime import datetime
from pytz import timezone
from mimetypes import guess_type

@login_required
# @transaction.atomic
def post_question(request):
    return render(request, 'discussion/discussion_board.html', {})


@login_required
# @transaction.atomic
def reply_question(request):
    return render(request, 'discussion/discussion_reply.html', context)


@login_required
# @transaction.atomic
def delete_post(request):
    return render(request, 'discussion/discussion_board.html', {})


@login_required
def discussion_home(request):
    posts = Post.objects.all().order_by('-post_time')
    post_replies = [];
    context={}
    i = len(posts)
    for post in posts:
        number_replies = len(Reply.objects.filter(reply_to = post).order_by('post_time'))
        post_replies.append({'post':post, 'number_replies' : number_replies, 'list_id' : i})
        i -= 1
    if Learner.objects.filter(user = request.user):
        learner = Learner.objects.get(user = request.user)
        flag= 0
       
    if Teacher.objects.filter(user = request.user):
        teacher = Teacher.objects.get(user = request.user)
        flag = 1

    context = {'username' : request.user.username, 'posts' : post_replies,'flag':flag}
    context['newmsgs'] = request.user.newmsg.all().order_by('-timestamp')
    context['msgcount'] = request.user.newmsg.all().count()
    if request.user.newmsg.filter(isReply=False):
        context['hasnewmsg'] = 'yes'
    else:
        context['hasnewmsg'] = 'no'
    return render(request, 'discussion/discussion_board.html', context)


@login_required
def discussion_reply(request, post_id):
    if not Post.objects.filter(id__exact = post_id):
        return HttpResponse("This post ID does not exist!")
    else:
        post = Post.objects.get(id__exact = post_id)
        learnerSet = Learner.objects.filter(user = post.author)
        if len(learnerSet) > 0:
            post_user = learnerSet[0]
        else:
            teacher = Teacher.objects.get(user = post.author)
            post_user = teacher

        replies = Reply.objects.filter(reply_to__id = post_id)
        max_reply_id = replies.aggregate(Max('id'))['id__max'] or 0
        user_temp = Learner.objects.filter(user = request.user)
        is_learner = len(user_temp)
        if is_learner == 1:
            cur_user = user_temp[0]
            flag = 0
        else:
            flag = 1
            cur_user = Teacher.objects.get(user = request.user)
        # print 'hello'
        return render(request, 'discussion/discussion_reply.html', \
            {'post': post, 'replies' : replies, 'post_user': post_user, 'max_reply_id' : max_reply_id,\
                'username' : request.user.username, 'cur_user' : cur_user,'flag':flag})


@login_required
def get_posts(request):
    all_posts = Post.objects.all().order_by('-post_time')
    post_replies = []
    i = len(all_posts)
    for post in all_posts:
        replies = Reply.objects.filter(reply_to__id = post.id).order_by('post_time')
        context_temp = {'post' : post, 'replies' : replies, 'list_id' : i, 'number_replies' : len(replies)}
        post_replies.append(context_temp)
        i -= 1
    context = {'post_replies' : post_replies}
    return render(request, 'discussion/posts.json', context, content_type = 'application/json')


@login_required
# @transaction.atomic
def post_post(request):
    form = PostFormForm(request.POST)
    if not form.is_valid():
        print 'form not valid'
        return render(request, 'discussion/post.json', {}, content_type='application/json')
    
    new_post = Post(title = form.cleaned_data['title'],\
        text = form.cleaned_data['text'], \
        post_time = form.cleaned_data['post_time'],\
        author = request.user)
    new_post.save()

    return render(request, 'discussion/post.json', \
        {'post': new_post}, content_type='application/json')


@login_required
# @transaction.atomic
def post_reply(request):
    usernameTemp = request.user.username
    userTemp = User.objects.get(username = usernameTemp)
    learnerSet = Learner.objects.filter(user = userTemp)
    if len(learnerSet) > 0:
        retUser = learnerSet[0]
    else:
        teacher = Teacher.objects.get(user = userTemp)
        retUser = teacher

    form = ReplyForm(request.POST)
    if not form.is_valid():
        print 'form not valid!'
        return render(request, 'discussion/reply.json', {}, content_type='application/json')

    to_post = Post.objects.get(id=form.cleaned_data['post_id'])

    new_reply = Reply(text = form.cleaned_data['text'], \
        post_time = form.cleaned_data['post_time'],\
        reply_to = Post.objects.get(id = form.cleaned_data['post_id']),\
        author = request.user)
    new_reply.save()
    
    return render(request, 'discussion/reply.json', {'reply': new_reply, 'user': retUser}, content_type='application/json')


@login_required
def get_postreply(request, post_id, max_reply_id):
    replies = Reply.objects.filter(reply_to__id = post_id).filter(id__gt = max_reply_id)
    return render(request, 'discussion/replies.json', {'replies' : replies}, content_type='application/json')


@login_required
def get_user_photo(request, user_id):
    learnerSet = Learner.objects.filter(user__id = user_id)
    if len(learnerSet) > 0:
        retUser = learnerSet[0]
    else:
        retUser = Teacher.objects.get(user__id = user_id)
    
    if not retUser.photo:
        raise Http404 
    content_type = guess_type(retUser.photo.name)
    return HttpResponse(retUser.photo, content_type = content_type)

@login_required
# @transaction.atomic
def delete_post(request, post_id):
    postTemp = Post.objects.get(id = post_id)
    replies = Reply.objects.filter(reply_to__id = post_id)
    postTemp.delete()
    for reply in replies:
        reply.delete()
    return redirect(reverse('discussion_home'))


@login_required
# @transaction.atomic
def delete_reply(request, reply_id):    
    replySet = Reply.objects.filter(id = reply_id)
    if len(replySet) > 0:        
        replyTemp = replySet[0]

        learnerSet = Learner.objects.filter(user = replyTemp.author)
        if len(learnerSet) > 0:
            retUser = learnerSet[0]
        else:
            retUser = Teacher.objects.get(user = replyTemp.author)

        post_id = replyTemp.reply_to.id
        replyTemp.delete()

        return render(request, 'discussion/empty.json', {'flag': 1}, content_type = 'application/json')
    else:
        return render(request, 'discussion/empty.json', {'flag' : 0}, content_type = 'application/json')
    


@login_required
def index(request):
    user = request.user
    if Learner.objects.filter(user__exact=user):
        flag = 0
    else:
        flag = 1
    RoomObj = ChatRoom.objects.all()
    if request.user.newmsg.filter(isReply=False):
        hasnewmsg = 'yes'
    else:
        hasnewmsg = 'no'
    return render(request, 'discussion/index.html', {'username': user.username, 'hasnewmsg':hasnewmsg,'RoomObj': RoomObj,'flag':flag,
                                                     'newmsgs':user.newmsg.all().order_by('-timestamp'),
                                                     'msgcount':user.newmsg.all().count()})


@login_required
def video_home(request):
    user = request.user
    if Learner.objects.filter(user__exact=user):
        flag = 0
    else:
        flag = 1
    VedioObj = VideoRoom.objects.all()
    if request.user.newmsg.filter(isReply=False):
        hasnewmsg = 'yes'
    else:
        hasnewmsg = 'no'
    return render(request, 'discussion/video_home.html', {'username': user.username, 'hasnewmsg':hasnewmsg,'RoomObj': VedioObj,'flag':flag,
                                                     'newmsgs':user.newmsg.all().order_by('-timestamp'),
                                                     'msgcount':user.newmsg.all().count()})


@login_required
def newVideoRoom(request):
    error = []
    if not 'roomname' in request.POST or not request.POST['roomname']:
        error.append('Room name is required.')
    if error:
        return render(request, 'discussion/video_home.html', {'error':error})
    name = request.POST['roomname']
    new_room = VideoRoom(roomname=name+" "+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),owner=request.user.username)
    new_room.save()
    return redirect("/discussion/video")


@login_required
def deleteVideoRoom(request,rid):
    if len(VideoRoom.objects.filter(id = rid))>0:
        roomObj = VideoRoom.objects.get(id__exact= rid)
        roomObj.delete()
    return redirect("/discussion/video")


@login_required
def room(request, room_id):
    if not room_id.isdigit():
        return HttpResponse('<h1>No room</h1>')
    if not ChatRoom.objects.filter(id=room_id):
        return HttpResponse('<h1>No room</h1>')
    user = request.user
    ishout_client.register_group(
        user.id,
        room_id
    )
    if request.user.newmsg.filter(isReply=False):
        hasnewmsg = 'yes'
    else:
        hasnewmsg = 'no'
    roomObj = ChatRoom.objects.get(id=room_id)
    chatpoolObj = ChatPool.objects.filter(roomname=roomObj)
    msglist = []
    for i in chatpoolObj:
        msglist.append(i)
        print i
    if Learner.objects.filter(user__exact=user):
        learner = Learner.objects.get(user__exact=user)
        learner.save()
        flag= 0
    else:
        teacher = Teacher.objects.get(user__exact=user)
        teacher.save()
        flag= 1
    roomObj = ChatRoom.objects.get(id=room_id)
    result = RoomAccount.objects.filter(username=user, roomname=roomObj)
    if not result:
        u = RoomAccount(username=user, roomname=roomObj)
        u.save()
    userlObj = RoomAccount.objects.filter(roomname=roomObj)
    userlist = []
    for i in userlObj:
        userlist.append(i.username)

    return render(request,'discussion/room.html', {'user': user, 'roomObj': roomObj,'flag': flag,
                                                   'userlist': userlist,'msglist':msglist,'hasnewmsg':hasnewmsg,
                                                       'newmsgs' :user.newmsg.all().order_by('-timestamp'),
                                                       'cur_username':user.username,'msgcount':user.newmsg.all().count()})

@login_required
def getmsg(request):
    roomid = request.GET.get('roomid')
    roomObj = ChatRoom.objects.get(id=roomid)
    chatpoolObj = ChatPool.objects.filter(roomname=roomObj)
    msglist = []
    for i in chatpoolObj:
        msglist.append(i.msg)
    return HttpResponse(json.dumps(msglist))

@login_required
def updatechat(request):
    roomid = request.GET.get('roomid')
    print roomid
    roomObj = ChatRoom.objects.get(id=roomid)
    chatpoolObj = ChatPool.objects.filter(roomname=roomObj)
    eastern = timezone('US/Eastern')
    fmt = '%b. %d, %Y, %I:%M %p.'
    msglist = []
    for i in chatpoolObj:
        list = {}
        list['sender'] = i.sender
        loc_time = i.time.astimezone(eastern)
        list['time'] = loc_time.strftime(fmt)
        list['msg'] = i.msg
        msglist.append(list)
    return HttpResponse(json.dumps(msglist))


@login_required
def putmsg(request):
    roomid, content = request.POST.get('roomid'), request.POST.get('content')
    roomObj = ChatRoom.objects.get(id=roomid)
    s = ChatPool(roomname=roomObj, msg=content)
    s.save()
    return HttpResponse("OK")

@login_required
def exituser(request):
    print "exituser"
    roomid, userid = request.POST.get('roomid'), request.POST.get('userid')
    roomObj = ChatRoom.objects.get(id=roomid)
    userObj = User.objects.get(id=userid)
    u = RoomAccount.objects.filter(username=userObj, roomname=roomObj)
    u.delete()
    ishout_client.unregister_group(
        userid,
        roomid
    )

    return HttpResponse("OK")

@login_required
def onlineuser(request):
    roomid, userid = request.GET.get('roomid'), request.GET.get('userid')
    roomObj = ChatRoom.objects.get(id=roomid)
    userObj = User.objects.get(id=userid)
    u = RoomAccount.objects.filter(username=userObj, roomname=roomObj)
    if not u:
        u = RoomAccount(username=userObj, roomname=roomObj)
        u.save()
    userlObj = RoomAccount.objects.filter(roomname=roomObj)
    userlist = []
    for i in userlObj:
        userlist.append(str(i.username))
    return HttpResponse(json.dumps(userlist))

@login_required
def newRoom(request):
    error = []
    if not 'roomname' in request.POST or not request.POST['roomname']:
        error.append('Room name is required.')
    if error:
        return render(request, 'discussion/index.html', {'error':error})
    name = request.POST['roomname']
    new_room = ChatRoom(roomname=name+" "+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),owner=request.user.username)
    new_room.save()
    return redirect("/discussion/chat")

@login_required
def deleteRoom(request,rid):
    if len(ChatRoom.objects.filter(id = rid))>0:
        roomObj = ChatRoom.objects.get(id__exact= rid)
        ishout_client.broadcast_group(
            rid,
            'deletechannel',
            data = {'roomname':roomObj.roomname}
        )
        roomObj.delete()
    return redirect("/discussion/chat")

@login_required
def updateRoom(request):
    rooms = ChatRoom.objects.all()
    json = {}
    json['rooms'] = []
    json['cur_username']=request.user.username
    for room in rooms:
        print room.roomname
        r = {'roomname': room.roomname, 'id': room.id, 'owner':room.owner}
        json['rooms'].append(r)
    return JsonResponse(json)

def send_message(request, room_id):
    text=request.POST.get('text')
    uname=request.POST.get('username')
    if len(text) > 0:
        roomObj = ChatRoom.objects.get(id=room_id)
        s = ChatPool(roomname=roomObj, msg=text, sender=uname)
        s.save()
        print room_id
        ishout_client.broadcast_group(
            room_id,
            'alerts',
            data = {'text':text,'username':uname}
        )
    return HttpResponse("OK")


@login_required
def testVideoRoom(request,rid):
    if Learner.objects.filter(user__exact=request.user):
        flag = 0
    else:
        flag = 1	
    return render(request, 'discussion/video_room.html', {'rid':rid,'username':request.user.username,'flag':flag})
