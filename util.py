import json
import requests
from sd_core.cache import cache_user_credentials

host = "http://localhost:7600/api"


def credentials():
    creds = cache_user_credentials("SD_KEYS")
    return creds

def retrieve_settings():
    global settings
    creds = credentials()
    sundail_token = ""
    if creds:
        sundail_token = creds["token"] if creds['token'] else None
    try:
        sett = requests.get(host + "/0/getallsettings",
                            headers={"Authorization": sundail_token})
        settings = sett.json()
        print(settings)
    except:
        settings = {}
    return settings


def add_settings(key, value):
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    data = json.dumps({"code": key, "value": value})
    requests.post(host + "/0/settings", data=data, headers=headers)
    retrieve_settings()
