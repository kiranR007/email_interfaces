from django import forms

class ListCreationForm(forms.Form):
    list_name = forms.CharField(label="List Name",max_length=100,widget=forms.TextInput(attrs={'class':"form-control"}))
    
    
    
class CampaignCreation(forms.Form):
    campaign_name = forms.CharField(max_length=100, required=True)
    template_type = forms.CharField(max_length=100, required=True)
    template_content = forms.CharField(widget=forms.Textarea, required=True)
    upload_file = forms.FileField(required=True)
    