import pymongo

MONGODB_URI = "mongodb://admin:5SOJklKd1PtTZSWbE0DkSySVRk6AFffv@panel7:27017,panel9:27017,panel10:27017/?authSource=admin&replicaSet=ICS-MongoDB-Rep&readPreference=secondaryPreferred&ssl=false"
EMAIL_MASTER_COL = "email_interface_django"
CAMPAIGN_MASTER = "email_campaign"
LIST_MASTER = "email_list"
TEMPLATE_COLL = "email_templates"
USER_CLLECTION = "email_users"


mongodb = pymongo.MongoClient(MONGODB_URI)
email_database = mongodb[EMAIL_MASTER_COL]
campaign_colection = email_database[CAMPAIGN_MASTER]
list_collection = email_database[LIST_MASTER]
template_Colection = email_database[TEMPLATE_COLL]
user_collection = email_database[USER_CLLECTION]

