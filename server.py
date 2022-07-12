from threadsnake.core import *
import gzip

set_log_config(LogLevel.ALL, LogColorMode.TITLE)

#log_info('ready', 'Test')

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

#app = Application(get_port(9090))
#for m in app_middlewares:
#    app.configure(m)
#for r in app_routers:
#    app.use_router(app_routers[r], r)    

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