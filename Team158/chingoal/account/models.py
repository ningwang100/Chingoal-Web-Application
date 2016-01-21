from django.db import models

from django.contrib.auth.models import User

class Learner(models.Model):
    user = models.OneToOneField(User, unique = True, related_name="learner_user")
    TITLE_CHOICES = (('A', 'Pupil'), ('B', 'Freshman'), ('C', 'Sophomore'), \
        ('D', 'Junior'), ('E', 'Senior'), ('F', 'Graduate'))
    LEVELS = (('0','Zero level'),('1','One level'),('2','Two levels'),('3','Three levels'),('4','Four levels'),('5','Five levels'))
              
    LESSONS = (('1','One lesson'),('2','Two lessons'),('3','Three lessons'),('4','Four lessons'),('5','Five lessons'))
                   
    title = models.CharField(max_length = 20, default = TITLE_CHOICES[0][1], choices = TITLE_CHOICES)
    progress_level = models.CharField(max_length = 20, default = LEVELS[0][1], choices=LEVELS)
    progress_lesson = models.CharField(max_length = 20, default = LESSONS[0][1], choices=LESSONS)
    
    current_level = models.IntegerField(default=0)
    current_lesson = models.IntegerField(default=1)

    user_vm = models.IntegerField(default = 0)
    lesson_plan = models.IntegerField(default = 1)  # MAX = 5
    follows = models.ManyToManyField(User,related_name = "learner_follows")
    bio = models.CharField(max_length = 420, default='Please introduce yourself')
    photo = models.ImageField(upload_to = 'portrait', blank = True, default = '/user_photo/portrait/default.jpg')
    unlock = models.IntegerField(default = 0)
    activation_key = models.CharField(max_length=40, blank=True)
    
    def __unicode__(self):
        return 'Learner' + self.user.username

class History(models.Model):
    user = models.ForeignKey(User, related_name="history")
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length = 100)
    kind = models.CharField(max_length=20)
    def __unicode__(self):
        return self.content

class Newmsg(models.Model):
    user = models.ForeignKey(User, related_name="newmsg")
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length = 420)
    sender = models.CharField(max_length = 40)
    isReply = models.BooleanField(default = False)
    def __unicode__(self):
        return self.text

class Teacher(models.Model):
    user = models.OneToOneField(User, unique = True, related_name="teacher")
    follows = models.ManyToManyField(User,related_name = "teacher_follows")
    bio = models.CharField(max_length = 420, default='Please introduce yourself')
    photo = models.ImageField(upload_to = 'portrait', blank = True, default = '/user_photo/portrait/default.jpg')
    activation_key = models.CharField(max_length=40, blank=True)
    
    def __unicode__(self):
        return 'Teacher' + self.user.username

