import random
import os
from locust import FastHttpUser, task, constant_pacing, run_single_user
import relocwsfunc
import relocredirectfunc

# ==============================================================================
# Relocator combined simulations for (redirect-endpoint and whitelabel-endpoint)
# ==============================================================================
relocate_testdata_whitelables = relocwsfunc.init_testdata_whitelables(
    os.path.dirname(os.path.abspath(__file__)) + "/relocate_ws_testdata.txt")
print(f"Loaded #{len(relocate_testdata_whitelables)} whitelables testdata sets")

# IKDhPmJcdw is a hash provided by DWH please make sure it is still valid for the next load-test
IDEALO_HOST_HEADERS = {'User-Agent': 'Relocator-AWS LOADTEST IKDhPmJcdw'}

AWS_WL_STG_HOSTNAME = "relocator.relocator-staging.aws.idealo.cloud"
STG_CLICK_HOSTNAME = "staging-click.idealo.com"

WL_TOKEN_URL = relocwsfunc.get_wl_oauth_token_url(STG_CLICK_HOSTNAME)
WL_URL = relocwsfunc.get_wl_url(STG_CLICK_HOSTNAME)
ALL_STG_SITES = relocwsfunc.init_stg_ws_sites(WL_TOKEN_URL)

# ====================================
# Redirect Endpoint support functions
# ====================================
# User-Agent handling moved to relocredirectfunc
REDIRECT_STAGING_HOST_HEADERS = {'X-Forwarded-For': '46.142.117.9'}

relocate_success_urls = relocredirectfunc.load_urls_from_file(os.path.dirname(os.path.abspath(__file__)) + "/relocate_success_urls.txt")
relocate_error_urls = relocredirectfunc.load_urls_from_file(os.path.dirname(os.path.abspath(__file__)) + "/relocate_error_urls.txt")
print("Loaded #" + str(len(relocate_success_urls)) + " success urls and #" + str(len(relocate_error_urls)) + " error urls")


# ==================================================================
# LOCUST CLASSES
# ==================================================================
class RelocatorCombinedLocust(FastHttpUser):
    network_timeout = 5.0
    connection_timeout = 5.0
    host = "https://relocator.relocator-staging.aws.idealo.cloud"
    # https://docs.locust.io/en/stable/api.html#module-locust.wait_time
    wait_time = constant_pacing(1)

    @task(5) # 5 percent of requests should be whitelables requests
    def post_ws(self):
        random_post_data = random.choice(relocate_testdata_whitelables)
        post_data_encoded = random_post_data.encode('utf-8')
        site_id = relocwsfunc.get_site_from_json(random_post_data)
        access_token = ALL_STG_SITES[site_id]["token"]
        site_name = ALL_STG_SITES[site_id]["name"]
        headers = IDEALO_HOST_HEADERS
        headers['Authorization'] = f"Bearer {access_token}"
        with self.client.post(WL_URL, name=site_name, headers=headers, data=post_data_encoded,
                              allow_redirects=False, catch_response=True) as response:
            if response.status_code == 401:
                print(f"Got 401 response - for url={WL_URL} site_name={site_name} site_id={site_id} access_token={access_token}")
                # try to get new credentials
                token = relocwsfunc.get_oauth_token(WL_TOKEN_URL, site_name, ALL_STG_SITES[site_id]["secret"])
                ALL_STG_SITES[site_id]["token"] = token
                print(f"Got 401 response - try to get new token for site={site_id} token={token}")
                response.failure(f"Got 401 response - try to get new token for site={site_id} token={token}")
            if response.status_code not in [200]:
                print(f"ERROR: status_code={response.status_code} url={response.url} headers={response.headers}")
            if (response.status_code == 200
                    and response.json() is None
                    or (response.json() is not None
                        and response.json()["clickBokey"] is None
                        and response.json()["url"] is None)):
                print(f"ERROR-RESULT-DETECTED: status_code={response.status_code} body={response.json()}")
                response.failure(f"Error Page from 200 response detected body={response.json()}")

    @task(90) # 90 percent of requests should be success pages
    def get_success_url(self):
        #next_reloc_url = relocredirectfunc.get_random_url(relocate_urls)
        next_reloc_url = relocredirectfunc.get_next_url(relocate_success_urls)
        headers, uri = relocredirectfunc.prepare_for_staging(next_reloc_url, REDIRECT_STAGING_HOST_HEADERS)
        headers = relocredirectfunc.generate_changing_useragent_string(headers)
        test_name = headers["X-Forwarded-Host"] + " (success url)"
        with self.client.get(uri, name=test_name, headers=headers, allow_redirects=False,
                             catch_response=True) as response:
            if response.status_code not in [301, 404]:
                if response is not None:
                    print("ERROR: status_code=" + str(response.status_code) + " url=" + response.url + " headers=" + str(
                        response.headers))
                else:
                    print("ERROR: response is None")

    @task(5) # 5 percent of requests should be error pages
    def get_error_url(self):
        #next_reloc_url = relocredirectfunc.get_random_url(relocate_urls)
        next_reloc_url = relocredirectfunc.get_next_url(relocate_error_urls)
        headers, uri = relocredirectfunc.prepare_for_staging(next_reloc_url, REDIRECT_STAGING_HOST_HEADERS)
        headers = relocredirectfunc.generate_changing_useragent_string(headers)
        test_name = headers["X-Forwarded-Host"] + " (error url)"
        with self.client.get(uri, name=test_name, headers=headers, allow_redirects=False,
                             catch_response=True) as response:
            if response.status_code == 404:
                # error pages should not be treated as load-testing errors
                response.success()
            if response.status_code not in [301, 404]:
                if response is not None:
                    print("ERROR: status_code=" + str(response.status_code) + " url=" + response.url + " headers=" + str(
                        response.headers))
                else:
                    print("ERROR: response is None")


# if launched directly, e.g. "python3 debugging.py", not "locust -f debugging.py"
if __name__ == "__main__":
    run_single_user(RelocatorCombinedLocust)
