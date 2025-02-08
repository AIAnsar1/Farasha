from requests_futures.sessions import FuturesSession
from time import monotonic

class FRSHFuturesSession(FuturesSession):
    def request(self, method, url, hooks=None, *args, **kwargs):
        if hooks is None:
            hooks = {}
        start = monotonic()

        def response_time(resp, *args, **kwargs):
            resp.elapsed = monotonic() - start

            return

        try:
            if isinstance(hooks["response"], list):
                hooks["response"].insert(0, response_time)
            elif isinstance(hooks["response"], tuple):
                # Convert tuple to list and insert time measurement hook first.
                hooks["response"] = list(hooks["response"])
                hooks["response"].insert(0, response_time)
            else:
                hooks["response"] = [response_time, hooks["response"]]
        except KeyError:
            hooks["response"] = [response_time]

        return super(FRSHFuturesSession, self).request(method, url, hooks=hooks, *args, **kwargs)