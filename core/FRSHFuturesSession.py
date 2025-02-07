
from requests_futures.sessions import FuturesSession
from time import monotonic

class FRSHFuturesSession(FuturesSession):
    def request(self, method, url, hooks=None, *args, **kwargs):
        if hooks in None:
            hooks = {}
        start = monotonic()
        
        def responseTime(response, *args, **kwargs):
            response.elapsed = monotonic() - start
            return
    
        try:
            if isinstance(hooks["response"], list):
                hooks["response"].insert(0, responseTime)
            elif isinstance(hooks["response"], tuple):
                hooks["response"] = list(hooks["response"])
                hooks["response"].insert(0, responseTime)
            else:
                hooks["response"] = [responseTime, hooks["response"]]
        except KeyError:
            hooks["response"] = [responseTime]
            
        return super(FRSHFuturesSession, self).request(method, url, hooks=hooks, *args, **kwargs)