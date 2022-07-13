from fileinput import filename
import shutil
from threadsnake.core import *
from threading import Thread
import zipfile
from html.parser import HTMLParser


class NuspecParse(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = ...) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.stack = [dict()]

    def get_current(self) -> Dict[str, Any]:
        return self.stack[-1:][0]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        current = self.get_current()
        newCurrent = dict()
        if attrs is not None:
            for kv in [(f'@{i[0]}', {"<text>":i[1]}) for i in attrs]:
                if not kv[0] in newCurrent:
                    newCurrent[kv[0]] = kv[1]
                else:
                    if not isinstance(newCurrent[kv[0]], list):
                        lst = newCurrent[kv[0]]
                        print(lst)
                        newCurrent[kv[0]] = [lst]
                    newCurrent[kv[0]].append(kv[1])
                    
        if not tag in current:
            current[tag] = newCurrent
        else:
            if not isinstance(current[tag], list):
                current[tag] = [current[tag]]
            current[tag].append(newCurrent)
        self.stack.append(newCurrent)
        return super().handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        self.stack.pop()
        return super().handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        data = data.strip()
        if len(data) == 0:
            return
        current = self.get_current()
        if '<text>' not in current:
            current['<text>'] = data
        else:
            if not isinstance(current['<text>'], list):
                current['<text>'] = [current['<text>']]
            current['<text>'].append(data)
        return super().handle_data(data)

    def sanitize(self, d:Dict[str, Any]):
        for k in d:
            if k == '<text>':
                continue
            if len(d[k]) == 1 and '<text>' in d[k] and not isinstance(d[k]['<text>'], list):
                d[k] = d[k]['<text>']
            else:
                d[k] = self.sanitize(d[k])
        return d

    def convert(self, data:str) -> Dict[str, Any]:
        self.stack = [dict()]
        #print(data)
        self.feed(data)
        return self.sanitize(self.stack.pop())

app:Router = export(__name__)

def get_nuget_data(fileLocation:str) -> Tuple[str, str, str]:
    with zipfile.ZipFile(fileLocation, 'r') as file:
        files = [i for i in file.namelist()]
        nuspecFileCandidates = [i for i in files if i.endswith('.nuspec') and '/' not in i]
        id:str = ''
        version:str = ''
        nuspecData = ''
        if len(nuspecFileCandidates) > 0:
            nuspecFileName = nuspecFileCandidates[0]
            nuspecData = ''
            with file.open(nuspecFileName) as nuspecFile:
                nuspecData = nuspecFile.read().decode('latin1')
                j = NuspecParse().convert(nuspecData)
                id = j['package']['metadata']['id']
                version = j['package']['metadata']['version']
        return id, version, nuspecData

def store_package(location:str, id:str, version:str):
    folder = os.sep.join(['nuget', id, version])
    os.makedirs(folder, exist_ok=True)
    fileName = os.sep.join([folder, f'{id}.{version}.nupkg'])
    shutil.move(location, fileName)

def upload_nuget(location:str):
    try:
        fileLocation:str = location['tempFilePath']
        id, version, nuspecData = get_nuget_data(fileLocation)
        store_package(fileLocation, id, version)
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