from threadsnake.core import *

app:Router = export(__name__)

@app.get('/{id}/{version}/index.json')
def flat_container(app:Application, req:HttpRequest, res:HttpResponse):
    res.end('Not found', 404)
    #{"versions":["0.0.1", "0.0.2"]}

@app.get('/{id}/{version}/{id2}.{version2}.nupkg')
def flat_container_download(app:Application, req:HttpRequest, res:HttpResponse):
    res.end('Not found', 404)
    #returns the file content

@app.get('/{id}/{version}/{id2}.nuspec')
def flat_container_download_nuspec(app:Application, req:HttpRequest, res:HttpResponse):
    res.end('Not found', 404)
    #returns xml nuspec