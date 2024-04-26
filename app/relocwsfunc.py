from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
import json


def get_oauth_token(token_url, client_id, client_secret):
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=token_url,
                              client_id=client_id, client_secret=client_secret)
    print(f"token for {client_id} token={token['access_token']}")
    return token['access_token']


def get_wl_oauth_token_url(hostname):
    return f"https://{hostname}/oauth/token"


def get_wl_url(hostname):
    return f"https://{hostname}/relocate/webservice"

def get_site_from_json(json_string):
    parsed = json.loads(json_string)
    site = parsed["site"]
    if site is None:
        site = "null"
    return site


def init_testdata_whitelables(testdata_filename):
    test_data_list = []
    with open(testdata_filename) as f:
        for testdata_line in f:
            test_data_list.append(testdata_line.strip())
    return test_data_list


# secrets
# you need to put secrets in a json file "oauth_secret.json" with following structure:
# {
#     "<site_id for preis_de it is null>" : {
#         "name": "PREIS_DE",
#         "secret": "<oauth-secret>",
#         "token": ""
#     }
# }
# the token will be set later
#
def init_stg_ws_sites(aws_stg_oauth_url):
    secret_file = os.path.dirname(os.path.abspath(__file__)) + "/oauth_secret.json"
    all_stg_sites = {}
    with open(secret_file) as f:
        all_stg_sites = json.load(f)

    # init OAuth tokens
    print("initializing OAuth tokens")
    for site_id in all_stg_sites:
        client_id = all_stg_sites[site_id]["name"]
        client_secret = all_stg_sites[site_id]["secret"]
        token = get_oauth_token(aws_stg_oauth_url, client_id, client_secret)
        all_stg_sites[site_id]["token"] = token
        print(f"New token for site={client_id} token={token}")

    return all_stg_sites