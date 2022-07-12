from threadsnake.core import *
from threading import Thread
import zipfile

app:Router = export(__name__)

def upload_nuget(location:str):
    try:
        fileLocation:str = location['tempFilePath']
        with zipfile.ZipFile(fileLocation, 'r') as file:
            files = [i for i in file.namelist()]
            nuspecFileCandidates = [i for i in files if i.endswith('.nuspec') and '/' not in i]
            if len(nuspecFileCandidates) > 0:
                nuspecFileName = nuspecFileCandidates[0]
                nuspecFileContent = ''
                with file.open(nuspecFileName) as nuspecFile:
                    nuspecFileContent = nuspecFile.read().decode('latin1')
            print(nuspecFileContent, files)
    except Exception as e:
        print(e)

#https://docs.microsoft.com/en-us/nuget/api/package-publish-resource
#@app.register_function('PUT', '/{package:re([\w_\-.]+)?}')
@app.register_function('PUT', '/')
#@validates_header('X-NuGet-ApiKey', lambda a: a == a)
def publish_put(app:Application, req:HttpRequest, res:HttpResponse):
    for r in req.files:
        Thread(target=lambda: upload_nuget(req.files[r])).start()
    res.end("OK", 200)

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