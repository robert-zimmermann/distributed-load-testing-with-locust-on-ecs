import re
import random


def add_host_to_headers(url, existing_headers):
    m = re.search(r'//([^/]+)', url)
    host = m.group()[2:]
    existing_headers['X-Forwarded-Host'] = host
    return existing_headers


def prepare_for_staging(url, existing_headers):
    headers = add_host_to_headers(url, existing_headers)
    uri = re.findall(r'https://www[^/]*(.*)', url)[0]
    return headers, uri


def generate_changing_useragent_string(existing_headers):
    global USER_AGENT_CHANGE_COUNTER
    # IKDhPmJcdw is a hash provided by DWH please make sure it is still valid for the next load-test
    existing_headers['User-Agent'] = 'Relocator-AWS LOADTEST IKDhPmJcdw ' + str(USER_AGENT_CHANGE_COUNTER)
    USER_AGENT_CHANGE_COUNTER += 1
    return existing_headers


def get_random_url(url_list):
    return random.choice(url_list)


def get_next_url(url_list):
    global URL_COUNTER
    next_reloc_url = url_list[URL_COUNTER]
    URL_COUNTER += 1
    if URL_COUNTER >= len(url_list):
        URL_COUNTER = 0
        #print("URL_COUNTER START AGAIN FROM 0")
    return next_reloc_url


def load_urls_from_file(urls_filename):
    urls = []
    with open(urls_filename) as f:
        for url in f:
            urls.append(url.strip())
    return urls

URL_COUNTER = 0
USER_AGENT_CHANGE_COUNTER = 1
