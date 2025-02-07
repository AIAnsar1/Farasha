


class FRSHQueryNotify:
    def __init__(self, result=None):
        self.result = result
        
    def start(self, message=None):
        pass
    
    def update(self, result=None):
        self.result = result
        
    def finish(self, message=None):
        pass
    
    def __str__(self):
        return str(self.result)
        