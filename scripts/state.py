import time
from urllib.parse import urlparse
from logger import Log

"""
state
0: Before start
1: detect the RP website's message
2: detect the IdP website's message for authorization
3: detect the RP website's message again
4: log in successfully
5: timeout
"""


class State():
    def __init__(self, web, logger: Log):
        self.current_web = ""  # 当前测试的网站
        self.state = 0  # 处于哪一个状态
        self.state_time = time.time()  # 状态更新时间
        self.have_state_para = set()
        self.state_para_checked = False
        self.logger = logger

    def set_current_web(self, web):
        self.current_web = web
        self.state = 0
        self.state_time = time.time()
        self.have_state_para = set()
        self.state_para_checked = False

    def set_state(self, new_state):
        self.state = new_state
        self.state_time = time.time()
        self.logger.write_info("set_state " + str(new_state))

    def renew_state(self, flow, IdP):
        # 0 to 1
        if self.state == 0 and self.current_web in flow.request.host:
            self.set_state(1)
            return 1
        # 1 to 2
        if IdP == "facebook.com":
            if self.state == 1 and "facebook.com" in flow.request.host:
                path = urlparse(flow.request.pretty_url).path
                if "/dialog/oauth" in path or "/x/oauth" in path:
                    self.set_state(2)
                    return 2
        if IdP == "api.twitter.com":
            if self.state == 1 and "api.twitter.com" in flow.request.host:
                path = urlparse(flow.request.pretty_url).path
                if "/oauth/authenticate" in path or "/x/oauth" in path:
                    self.set_state(2)
                    return 2
        # 2 to 3
        if self.state == 2 and self.current_web in flow.request.host:
            self.set_state(3)
            return 3
        # 3 to 4
        # realized in main.py
        return -1

    def timeout(self):
        if (time.time() - self.state_time) > 5:
            if self.state == 3:
                self.set_state(5)
            return True
        else:
            return False

    def confirm_state_para(self):
        self.have_state_para.add(self.state)

    def check_state_para(self):
        self.state_para_checked = True
        if self.have_state_para == {1, 2, 3}:
            return True
        else:
            return False
