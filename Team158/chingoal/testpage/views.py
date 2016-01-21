from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.views import password_reset, password_reset_confirm
# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
# from django.db.models import Q
# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db.models import Count
from django.db import transaction
from django.template import loader, Context
# from grumblr.models import *
from datetime import datetime
# from forms import *
from mimetypes import guess_type
from django.core.mail import send_mail
from django.conf import settings
from django.core import serializers
from account.models import *
from forms import *
from models import *

import urllib2
import random

from mimetypes import guess_type

@login_required
def homepage(request):
	context = {}
	return redirect('dashboard')

@login_required
def get_test(request,level):
	context = {}
	context['username'] = request.user.username
	cur_user = User.objects.get(username__exact = context['username'])
	learner = Learner.objects.get(user = cur_user)
	context['cur_user'] = learner
	context['level'] = level
	return render(request, 'testpage/test.html', context)

@login_required
def get_learn(request,level,lesson):
	context = {}
	context['username'] = request.user.username
	cur_user = User.objects.get(username__exact = context['username'])
	learner = Learner.objects.get(user = cur_user)
	context['cur_user'] = learner
	context['testoutlevel'] = level 

	learn_matrial = Learn.objects.get(level = level, lesson = lesson, chapter = 1)

	ltype = learn_matrial.ltype
	if ltype == 'text':
		context['learning_material'] = learn_matrial
		return render(request, 'testpage/learn.html', context)
	else:
		return render(request, 'testpage/learn_audio.html', context)

	# print learner.current_level

	# return render(request, 'testpage/learn.html', context)

@login_required
def get_result(request):
	# print request.POST
	context = {}
	context['username'] = request.user.username
	cur_user = User.objects.get(username__exact = context['username'])
	learner = Learner.objects.get(user = cur_user)
	context['cur_user'] = learner
	context['tid'] = request.POST['qid']
	curtest = TestAnswer.objects.get(tid=request.POST['qid'],username=request.user.username)
	curquestion = curtest.question.all()

	score = int(len(curquestion.filter(correctness='True'))*100/len(curquestion))
	level = int(request.POST['level'])
	if(score>60):
		# learner.user_vm += 10
		print "greater then 60"
		if level<5 and learner.current_level == level:
			learner.user_vm += 10
			learner.current_level = level + 1
			learner.current_lesson = 1
			print "level less than 5"
	learner.save()
	context['questionanswer'] = curquestion
	context['score'] = score
	return render(request, 'testpage/test-feedback.html', context)

@login_required
def question_result(request):
	tid = request.POST['tid']
	qid = int(request.POST['qid'])
	curtest = TestAnswer.objects.get(tid=tid,username=request.user.username)

	curanswer = QuestionAnswer.objects.get(qid=qid,username=request.user.username)
	question = Question.objects.get(id=qid)

	qtype = question.qtype

	if qtype=="tr":
		itemTemplate = loader.get_template('testpage/fb-tr.html')
	else:
		itemTemplate = loader.get_template('testpage/fb-mc.html')

	print question.answer

	item = itemTemplate.render({"item":question}).replace('\n','').replace('\"','\'') #More escaping might be needed
	return render(request, 'testpage/testcontent.json', {"item":item,"id":qid,"flag":0,"qnum":0,"max":1}, content_type='application/json')

@login_required
def test_create(request):
	context = {}
	context['username'] = request.user.username
	context['flag'] = 1
	context['chooselevel'] = TestLevelForm()

	cur_teacher = Teacher.objects.get(user=request.user)

	unposttest = Test.objects.filter(teacher=cur_teacher,postflag='false')
	if len(unposttest)==0:
		newtest = Test(postflag="false",teacher=cur_teacher)
		newtest.save()
		context['testid'] = newtest.id
	else:
		context['testid'] = unposttest[0].id
	return render(request, 'testpage/post_question.html', context)

@login_required
def test_collection(request):
	context = {}
	context['username'] = request.user.username
	context['flag'] = 1

	cur_teacher = Teacher.objects.get(user=request.user)
	tests = Test.objects.filter(teacher=cur_teacher)
	context['tests'] = tests
	return render(request, 'testpage/teachertestdash.html', context)

@login_required
def test_reviewpost(request,test_id):
	context = {}
	context['username'] = request.user.username
	context['flag'] = 1
	form = TestLevelForm()

	cur_teacher = Teacher.objects.get(user=request.user)

	allposttest = Test.objects.filter(teacher=cur_teacher,id=test_id)
	if len(allposttest)==0:
		print "didn't find"
		# newtest = Test(postflag="false",teacher=cur_teacher)
		# newtest.save()
		# context['testid'] = newtest.id
	else:
		print "find"
	form.fields["test_level"].initial = allposttest[0].level 
	context['chooselevel'] = form  
	context['testid'] = allposttest[0].id
	context['saveflag'] = allposttest[0].postflag
	return render(request, 'testpage/post_question.html', context)

@login_required
def test_editposttest(request,test_id):
	x = Test.objects.get(id=test_id)
	x.postflag="false"
	x.save()
	return render(request, 'testpage/item.json', {"item":"","id":0,"flag":1}, content_type='application/json')


@login_required
def test_deleteposttest(request,test_id):
	x = Test.objects.get(id=test_id)
	y = x.question.all().delete()
	x.delete()
	return render(request, 'testpage/item.json', {"item":"","id":0,"flag":1}, content_type='application/json')

@login_required
def test_unpost_question(request,id):
	# mc
	x = Question.objects.get(id=id)
	
	if x.qtype=="mc":
		itemTemplate = loader.get_template('testpage/unpost_mc.html')
		item = itemTemplate.render({"id":id,"form":MCQFrom()}).replace('\n','').replace('\"','\'') #More escaping might be needed
	else:
		itemTemplate = loader.get_template('testpage/unpost_tr.html')	
		item = itemTemplate.render({"id":id,"form":TRQFrom()}).replace('\n','').replace('\"','\'') #More escaping might be needed
	return render(request, 'testpage/item.json', {"item":item,"id":id,"flag":1}, content_type='application/json')

@login_required
def get_items(request,id):
	max_globalentry = 1;
	ctest = Test.objects.get(id=id)
	items = ctest.question.all()
	context = {"max_entry":max_globalentry, "flag":ctest.postflag ,"items":items}
	return render(request, 'testpage/items.json', context, content_type='application/json')


@login_required
def get_test_post_id(request):
	newtest = Test.objects.create()
	newtest.save()
	id = newtest.id
	print id
	return render(request, 'testpage/item.json', {"item":"","id":id,"flag":1}, content_type='application/json')

@login_required
def post_add_question_mc(request):
	itemTemplate = loader.get_template('testpage/base_mc.html')
	new_question = Question(qtype="mc",saveflag="false");
	new_question.save()
	maxid = new_question.id
	
	test_id = request.POST['testid']
	print "post_add_question_mc:"+test_id
	x = Test.objects.get(id=test_id)
	x.question.add(new_question)
	
	item = itemTemplate.render({"id":maxid,"form":MCQFrom()}).replace('\n','').replace('\"','\'') #More escaping might be needed
	return render(request, 'testpage/item.json', {"item":item,"id":maxid,"flag":1}, content_type='application/json')

@login_required
def post_add_question_tr(request):
	itemTemplate = loader.get_template('testpage/base_tr.html')
	new_question = Question(qtype="tr",saveflag="false");
	new_question.save()
	maxid = new_question.id

	test_id = request.POST['testid']
	x = Test.objects.get(id=test_id)
	x.question.add(new_question)
	
	item = itemTemplate.render({"id":maxid,"form":TRQFrom()}).replace('\n','').replace('\"','\'') #More escaping might be needed
	return render(request, 'testpage/item.json', {"item":item,"id":maxid,"flag":1}, content_type='application/json')

@login_required
def post_save_mc_question(request,id):
	mcqform = MCQFrom(request.POST);
	flag = 0
	if mcqform.is_valid():
		new_question = Question.objects.get(id=id)
		new_question.question=mcqform.cleaned_data['question']
		new_question.a=mcqform.cleaned_data['a']
		new_question.b=mcqform.cleaned_data['b']
		new_question.c=mcqform.cleaned_data['c']
		new_question.d=mcqform.cleaned_data['d']
		new_question.answer=request.POST['optionsRadiosInline']
		new_question.explanation=mcqform.cleaned_data['explanation']
		new_question.saveflag="true"
		new_question.save()
		flag = 1
	itemTemplate = loader.get_template('testpage/base_mc.html')
	item = itemTemplate.render({"id":id,"form":mcqform,"answerchoice":request.POST['optionsRadiosInline']}).replace('\n','').replace('\"','\'') #More escaping might be needed
	return render(request, 'testpage/item.json', {"item":item,"id":id,"flag":flag}, content_type='application/json')

@login_required
def post_save_tr_question(request,id):
	trqform = TRQFrom(request.POST);
	flag = 0
	if trqform.is_valid():
		new_question = Question.objects.get(id=id)
		new_question.question=trqform.cleaned_data['question']
		new_question.answer=trqform.cleaned_data['explanation']
		new_question.saveflag="true"
		new_question.save()
		flag = 1
	itemTemplate = loader.get_template('testpage/base_tr.html')
	item = itemTemplate.render({"id":id,"form":trqform}).replace('\n','').replace('\"','\'') #More escaping might be needed
	return render(request, 'testpage/item.json', {"item":item,"id":id,"flag":flag}, content_type='application/json')

@login_required
def test_edit_question(request,id):
	context = {}
	new_question = Question.objects.get(id=id)
	new_question.saveflag="false"
	new_question.save()
	return render(request, 'testpage/item.json', {"item":"","id":id,"flag":1}, content_type='application/json')


@login_required
def test_delete_question(request,id):
	try:
		x = Question.objects.get(id=id)
		x.delete()
	except Question.DoesNotExist:
		x = None
	return render(request, 'testpage/item.json', {"item":"","id":id,"flag":1}, content_type='application/json')



@login_required
def test_post(request,test_id):
	x = Test.objects.get(id=test_id)
	x.postflag="true"
	x.save()
	return render(request, 'testpage/item.json', {"item":"","id":0,"flag":1}, content_type='application/json')

@login_required
def test_set_level(request,test_id):
	x = Test.objects.get(id=test_id)
	form = TestLevelForm(request.POST)
	if form.is_valid():
		x.level = form.cleaned_data['test_level']
		x.save()
		flag = 1
		print "valid" + x.level
	else:
		flag = 0
	return render(request, 'testpage/item.json', {"item":"","id":0,"flag":flag}, content_type='application/json')

@login_required
def next_questions(request):
	# print request.POST

	currentlevel = int(request.POST['level'])

	form = TestFrom(request.POST)
	form.is_valid()
	qid = int(form.cleaned_data['qid'])
	qnum = int(form.cleaned_data['qnum'])
	
	# print correctness
	flag = 1
	finish = 0
	if qid==-1:
		qnum = 0
		learner = Learner.objects.get(user__exact = request.user)
		numtest = len(Test.objects.filter(level = currentlevel,postflag='true'))
		testindex = random.randint(0,numtest-1)
		newtest = Test.objects.filter(level = currentlevel)[testindex]
		qid = newtest.id
		question = newtest.question.all()[0]
		length = len(newtest.question.all())
		form = TestFrom()
		if len(TestAnswer.objects.filter(tid=qid,username=request.user.username))==0:
			print "create new testanswer"
			newanswer = TestAnswer(tid=qid,username=request.user.username);
			newanswer.save()
	else:
		newtest = Test.objects.get(id = qid)
		length = len(newtest.question.all())
		if form.is_valid():
			if qnum<length:
				curquestion = newtest.question.all()[qnum-1]
				question = newtest.question.all()[qnum]
			else:
				curquestion = newtest.question.all()[qnum-1]
				question = newtest.question.all()[0]
				finish = 1
			curtest = TestAnswer.objects.get(tid=qid,username=request.user.username)

			if len(QuestionAnswer.objects.filter(qid=curquestion.id,username=request.user.username))==0:
				curquestion = newtest.question.all()[qnum-1]
				correctness = form.cleaned_data['answer']== curquestion.answer
				curanswer = QuestionAnswer(qid=curquestion.id,username=request.user.username,correctness=correctness)
			else:

				curquestion = newtest.question.all()[qnum-1]

				curanswer = QuestionAnswer.objects.filter(qid=curquestion.id,username=request.user.username)[0]

			print form.cleaned_data['answer']
			print question.answer

			curquestion = newtest.question.all()[qnum-1]
			correctness = form.cleaned_data['answer']== curquestion.answer

			curanswer.answer = form.cleaned_data['answer']
			curanswer.correctness = correctness
			curanswer.save()
			curtest.question.add(curanswer)
			curtest.save()
			form = TestFrom()
		else:
			print "has error"
			qnum = qnum-1
			question = newtest.question.all()[qnum]
			flag = 0
	qtype = question.qtype
	qnum = qnum+1
	if qtype=="tr":
		itemTemplate = loader.get_template('testpage/test-tr.html')
	else:
		itemTemplate = loader.get_template('testpage/test-mc.html')

	item = itemTemplate.render({"item":question,"form":form,"finish":finish,"level":currentlevel}).replace('\n','').replace('\"','\'') #More escaping might be needed
	return render(request, 'testpage/testcontent.json', {"item":item,"id":qid,"flag":flag,"qnum":qnum,"max":length}, content_type='application/json')

@login_required
def learn_audio(request):
	context = {}
	return render(request, 'testpage/audio.html', context)

@login_required
def get_learning(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def get_learning(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def get_learningResult(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def skip_question(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def exit_learning(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def show_tips(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def get_discussion(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def create_learning(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def learning_add_question(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def learning_save_question(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def learning_edit_question(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def learning_delete_question(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)

@login_required
def learning_post(request):
	context = {}
	context['username'] = request.user.username
	return render(request, 'testpage/learn.html', context)


def upload_text_learn(request):
	learn = Learn(ltype = 'text')
	form = UploadTextLearnForm(request.POST, request.FILES, instance = learn)

	if request.method == 'GET':
		form = UploadTextLearnForm(instance = learn)
		context = {'form': form}
		return render(request, 'testpage/upload_text_learn.html', context)

	if not form.is_valid():
		context = {'form': form}
		return render(request, 'testpage/upload_text_learn.html', context)

	form.save()

	return render(request, 'testpage/upload_audio_learn.html', {})

def upload_audio_learn(request):
	learn = Learn(ltype = 'audio')
	form = UploadAudioLearnForm(request.POST, request.FILES, instance = learn)

	if request.method == 'GET':
		form = UploadAudioLearnForm(instance = learn)
		context = {'form': form}
		return render(request, 'testpage/upload_audio_learn.html', context)

	if not form.is_valid():
		context = {'form': form}
		return render(request, 'testpage/upload_audio_learn.html', context)

	form.save()

	return render(request, 'testpage/upload_text_learn.html', {})

@login_required
def learn_audio(request):
	context = {}
	context['username'] = request.user.username
	cur_user = User.objects.get(username__exact = context['username'])
	learner = Learner.objects.get(user = cur_user)
	context['cur_user'] = learner
	return render(request, 'testpage/learn_audio.html', context)


@login_required
def get_learn_photo(request, currLevel, currLesson, currChapter, choice):
	learning_material = Learn.objects.get(level = currLevel, lesson = currLesson, chapter = currChapter)

	if (choice == 'a'):
		learn_image = learning_material.image1
	elif (choice == 'b'):
		learn_image = learning_material.image2
	else:
		learn_image = learning_material.image3

	if not learn_image:
		raise Http404

	content_type = guess_type(learn_image.name)
	return HttpResponse(learn_image, content_type = content_type)

@login_required
def get_learn_json(request, currLevel, currLesson, currChapter):
	context = {}
	context['username'] = request.user.username
	cur_user = User.objects.get(username__exact = context['username'])
	learner = Learner.objects.get(user = cur_user)
	context['cur_user'] = learner	

	learning_material = Learn.objects.get(level = currLevel, lesson = currLesson, chapter = currChapter)

	context['learning_material'] = learning_material
	if (learning_material.ltype == 'audio'):
		# return render(request, 'testpage/learn_audio.html', context)
		return render(request, 'testpage/audio.json', context, content_type='application/json')
	else:
		return render(request, 'testpage/text.json', context, content_type='application/json')
		# return render(request, 'testpage/learn_audio.html', context)

@login_required
def write_history(request):
	user = request.user
	currLevel = request.POST['currLevel']
	currLesson = request.POST['currLesson']
	text = 'Finished Level ' + str(currLevel) + ' Lesson ' + str(currLesson)
	history = History.objects.create(user = user, content = text, kind = 'learn')
	history.save()
	return render(request, 'testpage/empty.json', {}, content_type='application/json')


# TODO might not needed
@login_required
def get_learn_audio(request, currLevel, currLesson):
	context = {}
	context['username'] = request.user.username
	cur_user = User.objects.get(username__exact = context['username'])
	learner = Learner.objects.get(user = cur_user)
	context['cur_user'] = learner

	learning_material = Learn.objects.get(level = currLevel, lesson = currLesson, chapter = 5)

	context['learning_material'] = learning_material
	return render(request, 'testpage/learn_audio.html', context)


@login_required
def upgrade_lesson(request):
	usernameTemp = request.user.username
	cur_user = User.objects.get(username = usernameTemp)
	learner = Learner.objects.get(user = cur_user)

	learner.current_lesson += 1
	learner.save()
	return render(request, 'testpage/empty.json', {}, content_type='application/json')

