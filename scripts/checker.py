import mitmproxy
from urllib.parse import urlparse
import re

websites = [
    # facebook
    "ask.fm",
    "biblegateway.com",
    "booking.com",
    "ebay.com",
    "entrepreneur.com",
    "etsy.com",
    "fifa.com",
    "lonelyplanet.com",
    "pastebin.com",
    "scoop.it",
    "twitch.tv",
    # twitter
    "kinja.com",
    "theonion.com",
    "jezebel.com",
    "medium.com"
    ]

def check_host(flow: mitmproxy.http.HTTPFlow):
    host = flow.request.host
    for site in websites:
        if site in host:
            return site
    return ""

def check_IdP(flow: mitmproxy.http.HTTPFlow, IdP):
    host = flow.request.host
    if IdP in host:
        return host
    return ""

# check if the host's path contain keywords
def check_host_path(flow: mitmproxy.http.HTTPFlow):
    path = urlparse(flow.request.pretty_url).path
    if path == "" or path == "/":
        return True
    keywords = ["account", "user", "login"]
    for word in keywords:
        if word in path:
            return True
    return False

# functions below return True means there's a vulnerability or something missed

def check_307(flow: mitmproxy.http.HTTPFlow):
    if flow.response.status_code == 307:
        return True
    return False

def check_TLS(flow: mitmproxy.http.HTTPFlow):
    if flow.request.scheme == "https":
        return False
    return True

# functions below return True means we find the target

def contain_state(flow: mitmproxy.http.HTTPFlow):
    # state may in query of url
    queries = urlparse(flow.request.pretty_url).query.split("&")
    for query in queries:
        if query.startswith("state=") and len(query) > 20:
            return True
    # state may in Location of cookies
    if "location" in flow.response.headers.keys():
        queries = urlparse(flow.response.headers["location"]).query.split("&")
        for query in queries:
            if query.startswith("state=") and len(query) > 20:
                return True
    if "Location" in flow.response.headers.keys():
        queries = urlparse(flow.response.headers["Location"]).query.split("&")
        for query in queries:
            if query.startswith("state=") and len(query) > 20:
                return True
    # state may in body
    try:
        if flow.response.text.find("state="):
            return True
        if flow.request.text.find("&") > -1:
            queries = flow.request.text.split("&")
            for query in queries:
                if query.startswith("state=") and len(query) > 20:
                    return True
        elif flow.request.text.find("{") > -1:
            pass
        elif flow.request.text.startswith("state=") and len(flow.request.text) > 20:
            return True
    except (ValueError, UnicodeDecodeError) as e:
        pass
    return False

# find a word in content, without alphabet, number, or _ nearby
def contain_user_info(content, uf):
    found = {}
    for word in uf:
        result = []
        indexes = find_all(content, word)
        for i in indexes:
            if i == 0 and not re.match("\W", content[i+len(word)]):
                    continue
            elif (i+len(word)) > (len(content)-1) and not re.match("\W", content[i-1]):
                    continue
            elif not re.match("\W", content[i-1]) or not re.match("\W", content[i+len(word)]):
                    continue
            result.append(i)
        if result:
            found[word] = result
    return found
        
# find all index of target in content
def find_all(content, target):
    result = []
    index = content.find(target)
    while index > -1:
        result.append(index)
        index = content.find(target, index+1)
    return result

    