class Redirector:
    def __init__(self, write_func):
        self.write_func = write_func

    def write(self, text):
        if text.strip():
            self.write_func(text.rstrip())

    def flush(self):
        pass