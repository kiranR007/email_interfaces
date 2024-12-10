from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import ListCreationForm,CampaignCreation
from django.contrib import messages
import requests,sys,json
from . models import List,Templates,Campaign
from .models import list_collection,campaign_colection,template_Colection,user_collection
from datetime import datetime,timedelta
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.views.decorators.cache import cache_control
# from django.contrib.auth.decorators import login_required
from functools import wraps
from django.http import JsonResponse
import pysftp,os


SENDY_URL = "https://api.email.smse.in/"

SENDY_API_KEY = "ji6MU8Tbob0bKERqDqX4"
brand_id = "1"
user_id = "1"

# SENDY_API_KEY = None
# brand_id = None
# user_id = None


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
print(BASE_DIR)


def index(request):
    return render(request,"demosendy/dashboard.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email and not password:
            messages.error(request,"Email and password required")
            return redirect("login_view")
        
        users = user_collection.find_one({'username': email})
        if users:
            if password == users.get("password"):
                
                request.session['brand_id'] = users.get("brand_id")
                request.session['SENDY_API_KEY'] = users.get("api_key")
                request.session['sendy_user_id'] = users.get("user_id")

                request.session['user_id'] = str(users['_id'])
                request.session['email'] = users['username']
                messages.success(request,"Login successful!")
                return redirect("all_campaigns")
            else:
                messages.error(request,"Invalid password")
        else:
            messages.error(request,"Invalid email or user does not exist.")
            
    return render(request, "demosendy/login.html")

def upload_the_file(file,campaign_id):
    print("uploading the file")
    path = "/upload/Kiran/Kiran2/SFTP/"
    sftp_target_path = os.path.join(path,str(campaign_id))
    
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    try:
        with pysftp.Connection(host="192.168.21.99",username="clmtest",password="yu2Ja2Ahf3baish",port=22,cnopts=cnopts) as sftp:
            print("sftp connected")
            
            if not sftp.exists(sftp_target_path):
                sftp.mkdir(sftp_target_path)
            # sftp.chdir(path)
            sftp.cwd(sftp_target_path)
            print(sftp.pwd)
            sftp.put(file)
            print("file uploaded")
    except Exception as e:
        print("file not uploaded exception occured ",str(e))
    
def save_file_locally(file,campaign_id):
    upload_path=os.path.join("media","campaign_files",str(campaign_id))
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    file_path = os.path.join(upload_path,file.name)
    with open(file_path,"wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path


def login_required(function):
    @wraps(function)
    def wrap(request,*args,**kwargs):
        if 'user_id' not in request.session:
            return redirect("login")
        return function(request, *args, **kwargs)
    return wrap 


@login_required
def create_list(request):
    if request.method == "POST":
        form = ListCreationForm(request.POST)
        if form.is_valid():
            list_name = form.cleaned_data['List Name']
            print(list_name)

            
            data ={
                "api_key":SENDY_API_KEY,
                "list_name":list_name,
                'list_type':'single_optin'
            }
            response = requests.post(SENDY_URL,data=data)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('status') == "success":
                    list_id = response_data.get('list_id')
                    messages.success(request,"List Created Successfully")
                    return render(request,"show_list.html",{'list_id':list_id,'list_name':list_name})    
                else:
                    messages.error(request,"Failed to create a list {}".format(response_data.get("message")))
            else:
                messages.error(request,"Failed to connect the sendy API")
            return redirect('create_list')
    else:
        form = ListCreationForm()
    return render(request,"demosendy/create_list.html",{'form':form})

@login_required
def create_campaign(request):
    SENDY_CAMPAIGN_URL = "https://api.email.smse.in/api/campaigns/create_campaign.php"
    attachment= ""
    username = request.session.get('email')
    
    brand_id = request.session.get('brand_id')
    send_user_id = request.session.get('sendy_user_id')
    api_key = request.session.get('SENDY_API_KEY')
    
    selected_template_id = None
    template_content = ''
    if request.method == "POST":
        if 'template_id' in request.POST:
            
            selected_template_id = request.POST.get('template_id')
            print(selected_template_id)
            if selected_template_id:
                template = template_Colection.find_one({'template_id': int(selected_template_id), 'username': username})
                print("templates ",template)
                if template:
                    template_content = template.get('template_content', '')
            lists = list_collection.find({'username': username}).sort("created_at", -1)
            templates = template_Colection.find({'username': username}).sort("created_at", -1)
            return render(request, "demosendy/create_campaign.html", {
                'lists': lists,
                'templates': templates,
                'template_content': template_content,
                'selected_template_id': selected_template_id
            })
            
        campaign_name = request.POST.get('campaign_name')
        template_type = request.POST.get('template_type')
        template_content = request.POST.get('template_content')
        image_upload = request.FILES.get('file_upload')
        list_name = request.POST.get('list_id')
        
        
        if not campaign_name  or not template_content or not list_name:
            messages.error(request,"All fields are required")
            return redirect('create_campaign')
        
        payload = {
            "api_key": api_key,
            "brand_id": brand_id,
            "list_id": list_name,
            "userID": send_user_id,
            "from_name": "Icsmobile",
            "from_email": "noreply@connect.icsmobile.in",
            "reply_to": "noreply@connect.icsmobile.in",
            "title": campaign_name,
            "html": template_content,
            "opens": "1",
            "clicks": "1"
        }
        
        json_payload = json.dumps(payload)
        print(json_payload)
        response = requests.post(SENDY_CAMPAIGN_URL,data=json_payload)
        if response.status_code == 200:
            response_data = response.json()
            print(response_data['campaign_id'])
            campaign_id = response_data['campaign_id']
            print(campaign_id)

            if image_upload:
                print("file exists")
                attachment = image_upload.name
                local_file_path = save_file_locally(image_upload,campaign_id)
                upload_the_file(local_file_path,campaign_id)
                
            payload ={
                "username":username,
                "campaign_id":campaign_id,
                "api_key": SENDY_API_KEY,
                "brand_id": brand_id,
                "list_id": list_name,
                "userID": user_id,
                "attachment":image_upload.name if image_upload else "",
                "from_name": "Icsmobile",
                "from_email": "noreply@connect.icsmobile.in",
                "reply_to": "noreply@connect.icsmobile.in",
                "title": campaign_name,
                "html": template_content,
                "opens": "1",
                "clicks": "1",
                "created_at":str(datetime.now())
                
            }
            campaign_colection.insert_one(payload)
            messages.success(request,"Campaign created Successfully")
        else:
            messages.error(request,"Campaign not found")

        return redirect("all_campaigns")
    lists = list_collection.find({'username':username}).sort("created_at", -1)
    templates = template_Colection.find({'username':username}).sort("created_at", -1)
    return render(request,"demosendy/create_campaign.html",{'lists':lists,"templates":templates})

@login_required
def log_download(request):
    return render(request,"demosendy/log_download.html")


def login(request):
    return render(request,"demosendy/login.html")

@login_required
def create_custom_fields(request,list_id):
    print(f"Request method: {request.method}")
    username = request.session.get('email')
    
    brand_id = request.session.get('brand_id')
    send_user_id = request.session.get('sendy_user_id')
    api_key = request.session.get('SENDY_API_KEY')
    
    SENDY_CUSTOM_URL = "https://api.email.smse.in/api/lists/add_custom_fields.php"
    if request.method == "POST":
        print(f"Request method: {request.method}")
        field_names = request.POST.getlist("field_name[]")
        data_types = request.POST.getlist("data_type[]")

       
        if not field_names or not data_types or len(field_names) !=  len(data_types):
            messages.error(request,"Both field name and data type required")
            return redirect('custom_fields',list_id=list_id)
        
        list_Record = list_collection.find_one({"encrypted_list_id": list_id,"username":username})
        print(list_Record)
        if not list_Record:
            messages.error(request, "List not found")
            return redirect('all_list')
        custom_fields = "$".join(field_names)
        custom_fields_for_mongo = [{"field_name": fn, "data_type": dt} for fn, dt in zip(field_names, data_types)]
        print(custom_fields_for_mongo)
        
        payload = {
            "api_key": api_key,  
            "brand_id":brand_id,                    
            "list_id": list_id,                 
            "custom_fields": custom_fields      
        }
        json_payload = json.dumps(payload)
        response = requests.post(SENDY_CUSTOM_URL,data=json_payload)
        response_data = response.json()
        response_data_response = response_data['response']
        # list_collection.update_one({'encrypted_list_id':list_id},{"$push":{'custom_fields':{'m$each':custo_fields}}})
        list_collection.update_one({'encrypted_list_id':list_id},{"$set":{'custom_fields':custom_fields_for_mongo,"remarks":str(response_data_response)}})
        messages.success(request,"Custom fields created Successfully")
        
            
        return redirect('all_list')
        
    return render(request, "demosendy/custom_fields.html", {'list_id': list_id})

@login_required
def all_campaigns(request):
    if request.method == "POST":
        username = request.session.get('email')
        if 'delete_campaign' in request.POST:
            print("deleting the camapign")
            camapign_id = request.POST.get('campaign_id')
            print(f"Received camapign_id: {camapign_id}")
            if camapign_id:
                try:
                    campaign_colection.delete_one({'campaign_id':int(camapign_id),"username":username})
                    messages.success(request,"campaign deleted successfully")
                except Exception as e:
                    messages.error(request, f"An error occurred while deleting the campaign: {str(e)}")
                return redirect('all_campaigns')
            else:
                messages.error(request, "Invalid camapign ID.")
            return redirect('all_campaigns')
        
    query = request.GET.get("search","")
    username = request.session.get('email')
    if query:
        filter_campaigns = list(campaign_colection.find({"username":username,"title": {"$regex":f"^{query}", "$options": "i"}})) 
    else:
        filter_campaigns =[]
    
    campaigns = list(campaign_colection.find({'username':username}))
    paginator = Paginator(campaigns,8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request,"demosendy/all_campaign.html",{'campaigns':campaigns,"filter_campaigns":filter_campaigns,"page_obj":page_obj})


@login_required
def all_list(request): 
    SENDY_URL = "https://api.email.smse.in/api/lists/add_list.php"
    username = request.session.get('email')
    
    brand_id = request.session.get('brand_id')
    send_user_id = request.session.get('sendy_user_id')
    api_key = request.session.get('SENDY_API_KEY')
    
    query = request.GET.get("search","")
    if request.method == "POST":
        if 'delete_list' in request.POST:
            print("delete method ")
            list_id = request.POST.get('list_id')
            print(f"Received list_id: {list_id}")
            if list_id:
                try:
                    list_collection.delete_one({"encrypted_list_id": list_id,"username":username})
                    messages.success(request, "List deleted successfully.")
                except Exception as e:
                    messages.error(request, f"An error occurred while deleting the list: {str(e)}")
                return redirect('all_list')
            else:
                messages.error(request, "Invalid list ID.")
            return redirect('all_list')
            
        else:
            
            list_name = request.POST.get("list_name")
            if not list_name:
                messages.error(request, "List name is required.")
                return redirect('all_list')
        
            payload = {
                "api_key":api_key,
                "list_name":list_name,
                "user_id":send_user_id,
                "brand_id":brand_id
            }
            json_payload = json.dumps(payload)
            try:
                print(json_payload,type(json_payload))
                response = requests.post(SENDY_URL,data=json_payload)
            
                if response.status_code == 200:
                    response_data = response.json()
                    print(response_data['data'])
                
                    if response_data.get("status") == "true":
                        list_id = response_data['data'].get('list_id')
                        encrypted_list_id = response_data['data'].get("encrypt_list_id")
                        list_Data = {
                            "username":username,
                            "list_id":list_id,
                            "encrypted_list_id":encrypted_list_id,
                            "list_name":list_name,
                            "created_at":str(datetime.now())
                        }
                        list_collection.insert_one(list_Data)
                        messages.success(request,"list created successfilly")
                        return redirect('custom_fields', list_id=encrypted_list_id)
                    else:
                        messages.error(request,"failed to create a list {}".format(response_data.get("message")))
                else:
                    messages.error(requests,"failed to connect the Sendy API")
                
            
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
            return redirect('all_list')
    
    if query:
        filtered_list = list(list_collection.find({'username':username,'list_name':{'$regex':f"^{query}","$options": "i"}}))
    else:
        filtered_list =[]
        
    
    lists = list(list_collection.find({'username':username}))
    paginator = Paginator(lists,8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"demosendy/all_list.html",{'lists':page_obj,'page_obj':page_obj,"filtered_list":filtered_list})

@login_required
def all_templates(request):
    username = request.session.get('email')
    query = request.GET.get("search","")
    if request.method == "POST":
        if 'delete_template' in request.POST:
            print("delete method of template")
            template_id = request.POST.get('template_id')
            print(f"Received list_id: {template_id}")
            if template_id:
                try:
                    print("enter to deleting mode")
                    template_Colection.delete_one({"template_id": int(template_id),"username":username})
                    messages.success(request, "Template deleted successfully.")
                except Exception as e:
                    messages.error(request, f"An error occurred while deleting the list: {str(e)}")
                return redirect('all_templates')
            else:
                messages.error(request, "Invalid list ID.")
            return redirect('all_templates')
        
        
    if query:
        filtered_template = list(template_Colection.find({'username':username,'template_name':{'$regex':f"^{query}","$options": "i"}}))
    else:
        filtered_template =[]
    
    all_template = list(template_Colection.find({"username":username}))
    paginator = Paginator(all_template,8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"demosendy/all_templates.html",{'templates':page_obj,'page_obj': page_obj,"filtered_template":filtered_template})

@login_required
def create_template(request):
    print(request.path)
    username = request.session.get('email')
    
    brand_id = request.session.get('brand_id')
    send_user_id = request.session.get('sendy_user_id')
    api_key = request.session.get('SENDY_API_KEY')
    
    SENDY_TEMPLATE_URL ="https://api.email.smse.in/api/campaigns/Create_template.php"
    if request.method == "POST":
        template_name = request.POST.get("template_name")
        template_content = request.POST.get("template_content")
        if template_name:
            template_payload = {
                "api_key":api_key,
                "brand_id":brand_id,
                "userID":send_user_id,
                "template_name":template_name,
                "html":template_content
            }
            print(template_payload)
            json_payload = json.dumps(template_payload)
            print(json_payload)
            
            try:
                response = requests.post(SENDY_TEMPLATE_URL,data=json_payload)
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('status') == "true":
                        template_id = response_data['template_id']
                        response = response_data['response']
                        template_data= {
                            "username":username,
                            "template_id":template_id,
                            "template_name":template_name,
                            "template_content":template_content,
                            "response":response,
                            "created_at":str(datetime.now())
                        }
                        template_Colection.insert_one(template_data)
                        messages.success(request,"template created successfilly")
                        return redirect('all_templates')
                    else:
                        messages.error(request,"failed to create a Templates {}".format(response_data.get("response")))
                else:
                    messages.error(requests,"failed to connect the Sendy API")
                return redirect("all_templates")
            except Exception as e:
                print(str(e))
    return render(request,"demosendy/create_template.html")



@login_required
def delete_list(request,list_id):
    lists = list_collection.find_one({'encrypted_list_id':list_id})
    if lists is not None:
        return render(request,"demosendy/delete_list.html",{"lists":lists})
    
    
@login_required    
def dashboard(request):
    return render(request,"demosendy/dashboard.html")


@login_required
def campaign_details(request, campaign_ids):
    try:
       
        camp_Details = campaign_colection.find_one({'campaign_id': int(campaign_ids)})
  
        if not camp_Details:
            messages.error(request, "Campaign not found")
            return redirect('all_campaigns')
        
        campaign_name = camp_Details.get('title',"")
        list_id = camp_Details.get('list_id',"")
        template_content = camp_Details.get('html',"")
        
        if list_id is  None:
            messages.error(request, "list not found")
            return redirect('all_campaigns')
            
        list_details = list_collection.find_one({'encrypted_list_id':list_id},{'list_name':1})
        list_name = list_details.get('list_name')
    
            
        return render(request, "demosendy/campaign_details.html", {'campaigns': camp_Details,"campaign_name":campaign_name,'list_name':list_name,'template_content':template_content})
    except Exception as e:
        messages.error(request, f"An error occurred Unable to fetch the campaign details")
        return redirect('all_campaigns')

        

@login_required
def list_details(request, encrypted_list_id):
    try:
        list_details = list_collection.find_one({"encrypted_list_id": encrypted_list_id})
        if not list_details:
            messages.error(request,"List not found.")
            return redirect('all_list')
        print(list_details)
        list_name = list_details.get('list_name',"")
        # custom_feilds = list_details.get('custom_fields','').split('$')
        custom_feilds = list_details.get('custom_fields',[])
        print(custom_feilds)
        return render(request, 'demosendy/list_details.html', {'lists': list_details,'custom_fields':custom_feilds,'list_name':list_name})
    except Exception as e:
        messages.error(request,f"An error occurred: {str(e)}")
        return redirect('all_list')
    
    



@login_required
def api_consumption(request):
    return render(request,"demosendy/api_consumption.html")

@login_required
def logs_download(request):
    query = request.GET.get("search","")
    username = request.session.get("email")
    if query:
        filter_campaigns = list(campaign_colection.find({"username":username,"title": {"$regex":f"^{query}", "$options": "i"}}))
        
    else:
        filter_campaigns =[]
    
    download =  request.GET.get("download")
    if download:
        pass
    campaigns = list(campaign_colection.find({"username":username}))
    paginator = Paginator(campaigns,8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request,"demosendy/logs_download.html",{'campaigns':campaigns,"filter_campaigns":filter_campaigns,"page_obj":page_obj})
    
    
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')



