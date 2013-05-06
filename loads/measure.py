import datetime
from requests.sessions import Session as _Session
from loads.stream import get_global_stream, set_global_stream
from loads.util import dns_resolve


class Session(_Session):

    def __init__(self, test):
        _Session.__init__(self)
        self.test = test

    def send(self, request, **kwargs):
        request.url, original, resolved = dns_resolve(request.url)
        request.headers['Host'] = original

        # started
        start = datetime.datetime.utcnow()
        res = _Session.send(self, request, **kwargs)
        res.started = start
        res.method = request.method
        if hasattr(self.test, 'current_cycle'):
            res.current_cycle = self.test.current_cycle
            res.current_user = self.test.current_user
        self._measure(res)
        return res

    def _measure(self, req):
        data = {'elapsed': req.elapsed,
                'started': req.started,
                'status': req.status_code,
                'url': req.url,
                'method': req.method}

        if hasattr(req, 'current_cycle'):
            data['cycle'] = req.current_cycle
            data['user'] = req.current_user

        stream = get_global_stream()

        if stream is None:
            stream = set_global_stream('stdout', {'stream_stdout_total': 1})

        stream.push(data)
