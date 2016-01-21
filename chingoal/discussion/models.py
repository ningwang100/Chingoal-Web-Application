from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User

from django.template import loader, Context

from account.models import *

class Post(models.Model):
    title = models.CharField(max_length=500)
    text = models.CharField(max_length=500)
    post_time = models.DateTimeField(auto_now_add = True)
    author = models.ForeignKey(User)
    # tag = models.CharField(max_length = 200)
    
    def __unicode__(self):
        return self.author + ',' + self.postTime

    @staticmethod
    def get_max_id():
        return Post.objects.all().aggregate(Max('id'))['id__max'] or 0

    @staticmethod
    def get_changed_posts(max_id):
        return Post.objects.filter(id__gt=max_id).distinct()

    # @property
    # def get_number_replies(self):
        # return len(Post.objects.filter(reply__reply_to = self))
        # return len(Reply.objects.filter(reply_to = self))

    @property
    def html(self):
        postTemplate = loader.get_template('discussion/post_base.html')
        context = Context({'post': self})
        return postTemplate.render(context).replace('\n','<br>').replace('"', '&quot;')


class Reply(models.Model):
    text = models.CharField(max_length=500)
    post_time = models.DateTimeField(auto_now_add = True)
    author = models.ForeignKey(User, related_name = 'author')
    reply_to = models.ForeignKey(Post, related_name = 'reply_to')
    
    def __unicode__(self):
        return self.author.username + (str)(self.post_time)

    @staticmethod
    def get_replies(postid):
        return Reply.objects.filter(post_id = postid)

    @property
    def html(self):
        replyTemplate = loader.get_template('discussion/reply_base.html')

        # user_temp = Learner.objects.filter(user = request.user)
        # is_learner = len(user_temp)
        # if is_learner == 1:
        #     cur_user = user_temp[0]
        # else:
        #     cur_user = Teacher.objects.get(user = request.user)
        # context = Context({'reply':self, 'cur_user': cur_user})

        context = Context({'reply': self})
        return replyTemplate.render(context).replace('\n','<br>').replace('"', '&quot;')


class ChatRoom(models.Model):
    roomname = models.CharField(max_length=100, unique=True)
    owner = models.CharField(max_length=100)
    def __unicode__(self):
        return self.roomname


class RoomAccount(models.Model):
    username = models.ForeignKey(User)
    roomname = models.ForeignKey(ChatRoom)
        
    def __unicode__(self):
        return unicode(self.username)


class ChatPool(models.Model):
    roomname = models.ForeignKey(ChatRoom)
    msg = models.CharField(max_length=1024)
    time = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=1024)
    def __unicode__(self):
        return unicode(self.roomname)

class VideoRoom(models.Model):
    roomname = models.CharField(max_length=100, unique=True)
    owner = models.CharField(max_length=100)
    def __unicode__(self):
        return self.roomname