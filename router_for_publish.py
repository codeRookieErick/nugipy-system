from threadsnake.core import *

app:Router = export(__name__)


#https://docs.microsoft.com/en-us/nuget/api/package-publish-resource
#@app.register_function('PUT', '/{package:re([\w_\-.]+)?}')
@app.register_function('PUT', '/')
#@validates_header('X-NuGet-ApiKey', lambda a: a == a)
def publish_put(app:Application, req:HttpRequest, res:HttpResponse):
    print(req.files)

@app.register_function('DELETE', '/{id}.{version}.nupkg/{id2}/{version2}')
@requires_parameters(['id', 'version', 'id2', 'version2'])
@validates_header('X-NuGet-ApiKey', lambda a: a == a)
def publish_delete(app:Application, req:HttpRequest, res:HttpResponse):
    res.end('Ok', 200)

@app.register_function('POST', '/{id}.{version}.nupkg/{id2}/{version2}')
@requires_parameters(['id', 'version', 'id2', 'version2'])
@validates_header('X-NuGet-ApiKey', lambda a: a == a)
def publish_relist(app:Application, req:HttpRequest, res:HttpResponse):
    res.end('Ok', 200)