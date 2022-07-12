from threadsnake.core import *

app:Router = export(__name__)

#https://docs.microsoft.com/en-us/nuget/api/registration-base-url-resource
@app.get('/registration/{id}/index.json')
def registration(app:Application, req:HttpRequest, res:HttpResponse):
    res.end('Not Found', 404)

@app.get('/registration/{id}/page/{lower}/{upper}.json')
@requires_parameters(['id', 'lower', 'upper'])
def registration_page(app:Application, req:HttpRequest, res:HttpResponse):
    res.end('Not Found', 404)

@app.get('/registration/{id}/leaf/{leaf}.json')
@requires_parameters(['id', 'leaf'])
def registration_leaf(app:Application, req:HttpRequest, res:HttpResponse):
    res.end('Not Found', 404)