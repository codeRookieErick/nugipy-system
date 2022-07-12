from threadsnake.core import *
import gzip

#set_log_config(LogLevel.ALL, LogColorMode.TITLE)

#log_info('ready', 'Test')

class Application2(Application):
    def __init__(self, port: int = 80, hostname: str = 'localhost', backlog: int = 5, readTimeout: float = 0.1, bufferSize: int = 1024):
        Application.__init__(self, port, hostname, backlog, readTimeout, bufferSize)

    def on_accept(self, client:socket.socket, address:str, readTimeout:int = None):
        self.on_receive(self.read(client, readTimeout), client, address)

    def read(self, client:socket.socket, readTimeout:int = None) -> bytes:
        data = []
        timeout = client.gettimeout()
        try:
            client.settimeout(readTimeout or self.readTimeout)
            while True:
                try:
                    buffer:bytes = client.recv(self.bufferSize)
                    if len(buffer) == 0:
                        break
                    data.extend(buffer)
                except:
                    break
        finally:
            client.settimeout(timeout)
        return bytes(data)

    def on_receive(self, data:bytes, clientPort:socket.socket, clientAddress):
        data_s = data.decode('latin1')
        if(len(data_s) == 0): return
        req = None
        res = HttpResponse()
        try:
            req = HttpRequest(data_s, clientAddress)
        except Exception as e:
            log_error(e) ##TOKEN TO FIND
            res.status(403, "BadRequest")
            clientPort.send(str(res).encode('latin1'))
            return
        
        if req.headers.get('Connection', '').lower() == 'keep-alive':
            chunk:bytes = self.read(clientPort, 2)
            if len(chunk) != 0:
                log_warning(f'{clientAddress} kept alive...')
                self.on_receive(b''.join([data, chunk]), clientPort, clientAddress)
                return
            else:
                log_success(f'{clientAddress} ended...')

        log_info(f'response pipeline created') ##TOKEN TO FIND
        stack = self.stack.copy()

        def next():
            if len(stack) > 0 and not res.ended:
                stack.pop()(self, req, res, next)
        
        if ':' in req.path:
            log_warning(f'potential query:pass params detected') ##TOKEN TO FIND
            pathParts = req.path.split('/')
            newPath = []
            for i in pathParts:
                queryPassParam = i.split(':')
                if len(queryPassParam) == 2:
                    log_load(f'query:pass param {queryPassParam[0]} resolved to {queryPassParam[1]}') ##TOKEN TO FIND
                    req.params[queryPassParam[0]] = queryPassParam[1]
                else:
                    newPath.append(i)
            req.path = '/'.join(newPath)

        if req.method in self.routes:
            log_success(f'method {req.method} found in registered routes') ##TOKEN TO FIND
            regularPaths = [i for i in self.routes[req.method]]
            for route in regularPaths:
                pattern = route
                pattern = re.sub(r"{([\w]+)\:int}", r"(?P<\1>[-]?[\\d]+)", pattern)
                pattern = re.sub(r"{([\w]+)\:float}", r"(?P<\1>[-]?[\\d]+[\\.]?[\\d]?)", pattern)
                pattern = re.sub(r"{([\w]+)\:re\(([\w\W]+?)\)}", r"(?P<\1>\2)", pattern)
                pattern = re.sub(r"{([\w]+)}", r"(?P<\1>[\\w]+)", pattern)
                pattern = "^" + pattern + "$"
                match = re.match(pattern, req.path)
                if match:
                    log_success(f'request {req.url} matches {route}') ##TOKEN TO FIND
                    handler = self.routes[req.method][route]
                    queryParams = match.groupdict()
                    for i in queryParams:
                        log_load(f'param {i} set to {queryParams[i]}') ##TOKEN TO FIND
                        req.params[i] = queryParams[i]
                    log_success(f'middleware for {route} add to pipeline') ##TOKEN TO FIND
                    def middleware(app, req, res, next):
                        res.status(200)
                        handler(app, req, res)
                        next()
                    stack.append(middleware)
                    break
        stack.reverse()
        log_info(f'pipeline begin') ##TOKEN TO FIND
        next()
        log_info(f'pipeline end') ##TOKEN TO FIND
        response:str = str(res).encode(res.encoding or 'latin1') #str(res).encode() if res.encoding is None else str(res).encode(res.encoding)
        clientPort.send(response)
        clientPort.close()


def test_middleware(app:Application, req:HttpRequest, res:HttpResponse, next:Callable):
    #print(req.raw)
    next()

app_middlewares = [
    test_middleware, 
    multipart_form_data_parser('temp'), 
    default_headers(lambda : {"Cache-Control":"nocache"}),
    body_parser
]

app_routers =     {
    '/search': routes_to('router_for_search'),
    '/flat-container': routes_to('router_for_listing'),
    '/publish': routes_to('router_for_publish'),
    '/registration': routes_to('router_for_registration'),
}

app = Application2(get_port(9090))
for m in app_middlewares:
    app.configure(m)
for r in app_routers:
    app.use_router(app_routers[r], r)    

app = build_application(get_port(9090), app_middlewares, app_routers)



def get_capabilities(baseUrl:str):
    return {
        "version":"3.0.0",
        "resources":[
            {
                "@id": f"{baseUrl}/flat-container",
                "@type": "PackageBaseAddress/3.0.0",
                "comment": "Base listing"
            },
            {
                "@id": f"{baseUrl}/publish",
                "@type": "PackagePublish/2.0.0",
                "comment": "Publishing"
            },
            {
                "@id": f"{baseUrl}/registration",
                "@type": "RegistrationsBaseUrl",
                "comment": "Registration"
            },
            {
                "@id": f"{baseUrl}/search",
                "@type": "SearchQueryService/3.0.0-beta",
                "comment": "Search"
            }
        ]
    }

def gzipify(data:str) -> str:
    return gzip.compress(data.encode('latin1')).decode('latin1')

@app.get('/index.json')
def main(app:Application, req:HttpRequest, res:HttpResponse):
    #create_headers(res)
    data = json.dumps(get_capabilities("http://localhost:9090"), indent=4)
    res.end(data, 200).content_type('application/json')

app.wait_exit()