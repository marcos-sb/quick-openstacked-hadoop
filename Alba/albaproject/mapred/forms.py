from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(max_length=20,
                             widget=forms.PasswordInput)

    
class JobForm(forms.Form):        
    server_name = forms.CharField(max_length=200)
    server_count = forms.IntegerField()
    flavor = forms.IntegerField(widget=forms.Select())
    file_input = forms.FileField()
    mapred_job = forms.FileField()
    fully_qualified_job_impl_class = forms.CharField(max_length=200)
