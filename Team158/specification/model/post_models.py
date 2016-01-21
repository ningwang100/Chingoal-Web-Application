from django.db import models

from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField()
    text = models.CharField()
    post_time = models.DateTimeField(auto_now_add = True)
    author = models.ForeignKey(User)
    tag = models.CharField(max_length = 200)
    
    def __unicode__(self):
        return self.author + ',' + self.postTime


class Reply(models.Model):
    text = models.CharField()
    post_time = models.DateTimeField(auto_now_add = True)
    author = models.ForeignKey(User)
    reply_to = models.ForeignKey(Post)
    
    def __unicode__(self):
        return self.author + ',' + self.postTime