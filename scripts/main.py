# HTTP lifecycle
import mitmproxy
from logger import Log
import checker
import time
from state import State
import serialize
import csrf
import os

log_file = "log/" + time.strftime('%m-%d %H:%M:%S ',time.localtime(time.time())) + str(os.getpid())
logger = Log(log_file)
logger.write_info("PID: " + str(os.getpid()))
cur_state = State("*", logger)
count = 0
access_token = ""

IdP = "api.twitter.com"
# IdP = "facebook.com"
logger.write_info("IdP: " + IdP)

def http_connect(flow: mitmproxy.http.HTTPFlow):
    """
        An HTTP CONNECT request was received. Setting a non 2xx response on
        the flow will return the response to the client abort the
        connection. CONNECT requests and responses do not generate the usual
        HTTP handler events. CONNECT requests are only valid in regular and
        upstream proxy modes.
    """

def requestheaders(flow: mitmproxy.http.HTTPFlow):
    """
        HTTP request headers were successfully read. At this point, the body
        is empty.
    """

def request(flow: mitmproxy.http.HTTPFlow):
    """
        The full HTTP request has been read.
    """
    global logger
    host = checker.check_host(flow)
    if host:
        if checker.check_TLS(flow):
            logger.write_info("[TLS] " + flow.request.pretty_url)


def responseheaders(flow: mitmproxy.http.HTTPFlow):
    """
        HTTP response headers were successfully read. At this point, the body
        is empty.
    """

def response(flow: mitmproxy.http.HTTPFlow):
    """
        The full HTTP response has been read.
    """
    global logger
    CSRF = csrf.CSRF(logger)
    host = checker.check_host(flow)

    # check 307 vulnerability
    if host:
        if checker.check_307(flow):
            logger.write_info("[307] " + flow.request.pretty_url)

    # check state parameters in traffic
    global cur_state
    # if the testing website change, reset c
    if host != cur_state.current_web and host:
        cur_state.set_current_web(host)
        logger.write_info("current_web: " + cur_state.current_web)

    cur_state.renew_state(flow, IdP)

    # check if state parameters shown at after state 2 
    if cur_state.state > 0 and cur_state.state < 4 and checker.contain_state(flow):
        cur_state.confirm_state_para()
        logger.write_info("found state= at state " + str(cur_state.state))

    # check if state parameters shown at after state 2
    if cur_state.state > 2 and cur_state.timeout() and not cur_state.state_para_checked:
        if not cur_state.check_state_para():
            logger.write_info("[STA] NO! " + cur_state.current_web)
        else:
            logger.write_info("[STA] OK! " + cur_state.current_web)

    # check if user info is shown, if so, login successfully
    if cur_state.state == 3:
        content = flow.response.text
        # string of username and its variation, like
        # user_info = ["Ross", "David", "ross", "david", "rossdavid", "RossDavid"]
        if IdP == "facebook.com":
            user_info = serialize.readbunchobj("user_info/fb_user_info")
            user_info2 = serialize.readbunchobj("user_info/fb_user_info2")
        if IdP == "api.twitter.com":
            user_info = serialize.readbunchobj("user_info/twitter_user_info")
            user_info2 = serialize.readbunchobj("user_info/twitter_user_info2")
        keywords = checker.contain_user_info(content, user_info)
        keywords2 = checker.contain_user_info(content, user_info2)
        if keywords:
            logger.write_info("found user info: " + str(keywords.keys()) + "\n       URL: " + flow.request.pretty_url)
            logger.write_info("[CSRF] Succeed, but login with origin user")
            cur_state.set_state(4)
        elif keywords2:
            logger.write_info("found user info: " + str(keywords2.keys()) + "\n       URL: " + flow.request.pretty_url)
            logger.write_info("[CSRF] Succeed")
            cur_state.set_state(4)
        else:
            cur_state.timeout(log_file)

    # record important flow
    global count
    if cur_state.state > 1:
        if (host and checker.check_host_path(flow)) or checker.check_IdP(flow, IdP):
            if "longming" in flow.request.headers.keys():
                serialize.writeBunchobj("Req2/" + str(count) + "-" + str(cur_state.state), flow.request)
                serialize.writeBunchobj("Res2/" + str(count) + "-" + str(cur_state.state), flow.response)
            else:
                serialize.writeBunchobj("Req/" + str(count) + "-" + str(cur_state.state), flow.request)
                serialize.writeBunchobj("Res/" + str(count) + "-" + str(cur_state.state), flow.response)
            count += 1

    # csrf
    if "facebook.com" in flow.request.pretty_url:
        target = "access_token="
        CSRF.csrf_substitude_code_in_text(target, flow)

        target = "code="
        CSRF.csrf_substitude_code_in_location(target, flow)

        target = "fb-ar"
        CSRF.csrf_substitude_header(target, flow)

    if "api.twitter.com" in flow.request.pretty_url:
        # target = "oauth_verifier="
        # CSRF.csrf_substitude_code_in_text(target, flow)

        target = "state="
        CSRF.csrf_substitude_code_in_text(target, flow)

        # if checker.check_host(flow):
        #     CSRF.csrf_substitude_code_in_location("oauth_token=", flow)


def error(flow: mitmproxy.http.HTTPFlow):
    """
        An HTTP error has occurred, e.g. invalid server responses, or
        interrupted connections. This is distinct from a valid server HTTP
        error response, which is simply a response with an HTTP error code.
    """