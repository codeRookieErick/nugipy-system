from threadsnake.core import *
import sqlite3

app:Router = export(__name__)
#https://docs.microsoft.com/en-us/nuget/api/search-query-service-resource
#q, skip, take, prerelease, semVerLevel, packageType
@app.get('/')
def search(app:Application, req:HttpRequest, res:HttpResponse):
    q:str = req.params.get('q', None)
    skip:int = int(req.params.get('skip', '0'))
    take:int = int(req.params.get('take', '0'))
    search_packages(q, skip, take)
    hits = [i for i in os.listdir('nuget') if q.lower() in i.lower()]
    print(os.listdir('nuget'))
    res.json({"totalHits":0, "data":[]})

def search_packages(q:str, skip:int, take:int):
    query = f"select * from versions where id like '%{q}%' order by id, version limit {take} offset {skip};"
    data = []
    with sqlite3.connect('database.db') as c:
        data = c.execute(query).fetchall()
    result = {"totalHits":len(data)}