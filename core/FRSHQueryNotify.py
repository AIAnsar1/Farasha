


class FRSHQueryNotify:

    def __init__(self, result=None):
        self.result = result
        # return

    def start(self, message=None):
        pass
    # return

    def update(self, result):
        self.result = result


    def finish(self, message=None):
        pass
        # return

    def __str__(self):
        return str(self.result)
        