from django.db import models
from db_connections import mongodb
# Create your models here.
from django.db import models


CAMPAIGN_MASTER = "email_campaign"
LIST_MASTER = "email_list"
TEMPLATE_COLL = "email_templates"
EMAIL_MASTER_COL = "email_interface_django"
USER_CLLECTION = "email_users"


email_database = mongodb[EMAIL_MASTER_COL]
campaign_colection = email_database[CAMPAIGN_MASTER]
list_collection = email_database[LIST_MASTER]
template_Colection = email_database[TEMPLATE_COLL]
user_collection = email_database[USER_CLLECTION]

class List(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} created at {self.created_at}"


class Templates(models.Model):
    template_name = models.CharField(max_length=255)
    template_Content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.template_name} created at {self.created_at}"
    
    
class Campaign(models.Model):
    campaign_name = models.CharField(max_length=255)
    template_name = models.CharField(max_length=255)
    template_content = models.TextField()
    file = models.FileField(upload_to="campaign_files/",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.campaign_name