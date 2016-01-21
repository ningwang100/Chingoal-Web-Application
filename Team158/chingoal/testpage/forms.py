from django import forms

class MCQFrom(forms.Form):
    question = forms.CharField(max_length=200,widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Choice Text'}))
    a = forms.CharField(max_length=200,widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Choice Text'}))
    b = forms.CharField(max_length=200,widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Choice Text'}))
    c = forms.CharField(max_length=200,widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Choice Text'}))
    d = forms.CharField(max_length=200,widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Choice Text'}))
    explanation = forms.CharField(max_length=200,widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Explanation'}))
    def clean(self):
        cleaned_data = super(MCQFrom, self).clean()
        return cleaned_data

class TRQFrom(forms.Form):
    question = forms.CharField(max_length=200,widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Question'}))
    explanation = forms.CharField(max_length=200,widget = forms.TextInput(attrs={'class':'form-control','placeholder':'Answer'}))
    def clean(self):
        cleaned_data = super(TRQFrom, self).clean()
        return cleaned_data

class TestLevelForm(forms.Form):
    LEVELS = (
        ('0','Zero level'),
        ('1','One level'),
        ('2','Two levels'),
        ('3','Three levels'),
        ('4','Four levels'),
        ('5','Five levels'),
    )

    test_level = forms.ChoiceField(choices=LEVELS, label="Test Level", widget=forms.Select())

    def clean(self):
        cleaned_data = super(TestLevelForm, self).clean()
        return cleaned_data


class TestFrom(forms.Form):
    answer = forms.CharField(max_length=200,widget = forms.TextInput(attrs={'class':'form-control'}))
    max_entry = forms.CharField(widget = forms.TextInput(attrs={'type':'hidden','id':'maxentry','value':'-1'}))
    qnum = forms.CharField(widget = forms.TextInput(attrs={'type':'hidden','id':'qnum','value':'-1'}))
    qid = forms.CharField(widget = forms.TextInput(attrs={'type':'hidden','id':'qid','value':'-1'}))
   
    def clean(self):
        # Checks the validity of the form data
        cleaned_data = super(TestFrom, self).clean()
        return cleaned_data

