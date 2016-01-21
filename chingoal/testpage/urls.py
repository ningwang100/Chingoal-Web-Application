
from django.conf.urls import include, url
from django.core.urlresolvers import reverse

urlpatterns = [
    url(r'^$','testpage.views.homepage',name ='gobackhomepage'),
    # url(r'^photo/(?P<username>.+)','grumblr.views.get_photo',name='photo'),
    url(r'^get-test/(?P<level>[0-5]{1})$','testpage.views.get_test',name ='gettest' ),
    url(r'^get-learn/(?P<level>[0-5]{1})/(?P<lesson>[1-6]{1})$','testpage.views.get_learn',name ='getlearn' ),
    url(r'^get-result$','testpage.views.get_result',name ='getresult' ),
    url(r'^test-create$','testpage.views.test_create',name ='testcreate' ),
    url(r'^test-add-q-mc$','testpage.views.post_add_question_mc',name ='testaddmcq' ),
    url(r'^test-add-q-tr$','testpage.views.post_add_question_tr',name ='testaddtrq' ),
    url(r'^test-save-mcquestion/(?P<id>[0-9]*)$','testpage.views.post_save_mc_question',name ='testsavemcquestion' ),
    url(r'^test-save-trquestion/(?P<id>[0-9]*)$','testpage.views.post_save_tr_question',name ='testsavetrquestion' ),
    url(r'^test-edit-question/(?P<id>[0-9]*)$','testpage.views.test_edit_question',name ='testeditquestion' ),
    url(r'^test-unpost-question/(?P<id>[0-9]*)$','testpage.views.test_unpost_question',name ='testunpostquestion' ),
    url(r'^get-items/(?P<id>[0-9]*)$','testpage.views.get_items',name ='getitems' ),
    url(r'^get-test-post-id$','testpage.views.get_test_post_id',name ='gettestpostid' ),
    url(r'^test-delete-question/(?P<id>[0-9]*)$','testpage.views.test_delete_question',name ='testdeletequestion' ),
    url(r'^test-post/(?P<test_id>[0-9]*)$','testpage.views.test_post',name ='testpost' ),
    url(r'^test-level/(?P<test_id>[0-9]*)$','testpage.views.test_set_level',name ='testsetlevel' ),
    url(r'^get-learningResult$','testpage.views.get_learningResult',name ='getlearningResult' ),
    url(r'^skip-question$','testpage.views.skip_question',name ='skipquestion' ),
    url(r'^exit-learning$','testpage.views.exit_learning',name ='exitlearning' ),
    url(r'^show-tips$','testpage.views.show_tips',name ='showtips' ),
    url(r'^get-discussion$','testpage.views.get_discussion',name ='getdiscussion' ),
    url(r'^create-learning$','testpage.views.create_learning',name ='createlearning' ),
    url(r'^learning-add-question$','testpage.views.learning_add_question',name ='learningaddquestion' ),
    url(r'^learning-save-question$','testpage.views.learning_save_question',name ='learningsavequestion' ),
    url(r'^learning-edit-question$','testpage.views.learning_edit_question',name ='learningeditquestion' ),
    url(r'^learning-delete-question$','testpage.views.learning_delete_question',name ='learningdelete_question' ),
    url(r'^learning-post$','testpage.views.learning_post',name ='learningpost' ),
    url(r'^next-questions$','testpage.views.next_questions',name ='nextquestions' ),
    url(r'^question-result$','testpage.views.question_result',name ='questionresult'),
    url(r'^audio$','testpage.views.learn_audio',name ='audio'),

    url(r'^get-learn-photo/(?P<currLevel>[0-9]*)/(?P<currLesson>[0-9]*)/(?P<currChapter>[0-9]*)/(?P<choice>[abc])$', 'testpage.views.get_learn_photo', name='getlearnphoto'),
    url(r'^get-learn-json/(?P<currLevel>[0-9]*)/(?P<currLesson>[0-9]*)/(?P<currChapter>[0-9]*)$', 'testpage.views.get_learn_json', name = 'getlearnjson'),
    # url(r'^write-history/(?P<currLevel>[0-9]*)/(?P<currLesson>[0-9]*)$', 'testpage.views.write_history', name = 'writehistory'),
    url(r'^write-history$', 'testpage.views.write_history', name = 'writehistory'),
    url(r'^get-learn-audio/(?P<currLevel>[0-9]*)/(?P<currLesson>[0-9]*)$', 'testpage.views.get_learn_audio', name = 'getlearnaudio'),
    url(r'^upgrade-lesson$', 'testpage.views.upgrade_lesson', name = 'upgradelesson'),

    # This is for uploading text learn
    url(r'^upload-text-learn$','testpage.views.upload_text_learn',name='uploadtextlearn'),
    url(r'^upload-audio-learn$','testpage.views.upload_audio_learn',name='uploadaudiolearn'),

    url(r'^test-reviewpost/(?P<test_id>[0-9]*)$','testpage.views.test_reviewpost',name='testreviewpost'),
    url(r'^test-editposttest/(?P<test_id>[0-9]*)$','testpage.views.test_editposttest',name='testeditposttest'),
    url(r'^test-deleteposttest/(?P<test_id>[0-9]*)$','testpage.views.test_deleteposttest',name='testdeleteposttest'),

    url(r'^test-collection$','testpage.views.test_collection',name='testcollection'),
    # This is for presentation
    url(r'^learn-audio$','testpage.views.learn_audio', name = 'learnaudio'),

    
]
