from django import forms

class NameForm(forms.Form):
	search_query = forms.CharField(label='Your Search Term', max_length=500)