Project proposal feedback
==================

**Team number**: 158
**Team name**: chingoal
**Team members**: [jgong1, jqiang, mingdaz, ningw]

### Charlie

Based on both your project proposal and your specification, I only slightly share the concern (voiced by some TAs below) that your project is too small.  In its currently-specified form, the project might be slightly too small for a four-person team.  This can be easily fixed, though, if you are sure to include rich content types (such as video or audio) in some of your media, such as audio-related features in your quizzes.  

An excellent feature---and an easy extension given your design---would be questions that require the user to read some Chinese word or phrase as part of the quiz.  Your web application could then record (i.e. store on the server) the audio of the user reading the word or phrase, and the teacher/grader could then access (using a different interaction in the web app) the stored audio to evaluate the student's work.  Doing this well would have you learn part of the HTML5 audio API, as well as the upload, storage, and download of rich media types.  You could additionally extend this with real-time features (interactive audio or video), but it's not clear you need to accomplish that for a four-person project.


### Andrew

You might want to look into how you want to serve your miscellaneous media (videos, articles, audio) as it's possible a lot this won't be hosted on your site. If it is hosted on your site, you'd have to work a little harder to achieve a similar level of functionality as you would for just linking/embedding media. Looking into websockets might also be useful for implementing real time chat. Additionally, your site will be sort of focused on seeding content to your site with the appropriate lessons and whatnot, so try to create lesson before hand to see how exactly you'd like them to be represented on the site. It might also be worth looking at Duolingo as reference for how a good language learning tool would look like.

### Shuai

Your project idea is fun and practical. However, upon looking through your proposed features, the workload is clearly too small for a team of four. I strongly recommend that you further define which additional features you will include in your project implementation, and obtain feedback from the course staff---especially Charlie---on the size and scope of your project before starting your implementation.

### Brian

Delivering different types of media over HTTP (video, audio, chinese characters) will give experience with content types. You could also use javascript to capture and upload audio from the device's microphone to test speaking skills.  Look into [getUserMedia()](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/getUserMedia).  I like the idea of earning points and leveling up for correct answers.  For extra features to increase scope, look at duolingo.com.  They have a similar achievement system.



---

To view this file with formatting, visit the following page: https://github.com/CMU-Web-Application-Development/158/blob/master/feedback/proposal.md
