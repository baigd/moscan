from mitmproxy import ctx

class Log():

    def __init__(self, log_file):
        self.log_file = log_file

    def info(self, str):
        ctx.log.info(str)

    def write_info(self, content):
        with open(self.log_file, 'a+') as f:
            f.write("\n[INFO] " + content)

    def write_error(self, content):
        with open(self.log_file, 'a+') as f:
            f.write("\n[ERROR] " + content)

    def write_file(self, file, content):
        with open(file, 'w+') as f:
            f.write(content)