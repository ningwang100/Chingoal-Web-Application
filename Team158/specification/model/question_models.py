from django.db import models

# Create your models here.
class Word_Translation(models.Model):
	question = models.CharField(max_length=200)
	answer = models.CharField(max_length=200)
	explanation = model.CharField(max_length=200)
	def __unicode__(self):
		return self.text

class Multiple_Choice(models.Model):
	question = models.CharField(max_length=200)
	a = models.CharField(max_length=200)
	b = models.CharField(max_length=200)
	c = models.CharField(max_length=200)
	d = models.CharField(max_length=200)
	answer = models.CharField(max_length=200)
	explanation = model.CharField(max_length=200)
	def __unicode__(self):
		return self.text


class Test(models.Model):
	lock = models.IntegerField()	
	MCq = models.ManyToManyField(Word_Translation)
	WTq = models.ManyToManyField(Multiple_Choice)
	def __unicode__(self):
		return self.text


class Learn(models.Model):
	lock = models.IntegerField()
	MCq = models.ManyToManyField(Word_Translation)
	WTq = models.ManyToManyField(Multiple_Choice)
	def __unicode__(self):
		return self.text
