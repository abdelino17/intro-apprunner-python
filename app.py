import fastapi, uvicorn
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.requests import Request
import prometheus_client
import time, random, os

api = fastapi.FastAPI()
api.mount('/static', StaticFiles(directory='assets'), name='static')
templates = Jinja2Templates(directory="templates")

REQUESTS = prometheus_client.Counter(
    'requests', 'Application Request Count',
    ['endpoint']
)

TIMER = prometheus_client.Histogram(
    'slow', 'Slow Requests',
    ['endpoint']
)

@api.get('/')
def index(request: Request):
    REQUESTS.labels(endpoint='/').inc()
    return templates.TemplateResponse("index.html", { 'request': request })

@api.get('/database')
def database():
    with TIMER.labels('/database').time():
        time.sleep(random.uniform(1, 2))
    return fastapi.responses.HTMLResponse(content="<h3>Completed expensive database operation from WeShare 2021</h3>")


@api.get('/metrics')
def metrics():
    return fastapi.responses.PlainTextResponse(
        prometheus_client.generate_latest()
    )

if __name__ == "__main__":
    print("Starting ...", os.getenv("APP_NAME", "none"))
    uvicorn.run(
        api, 
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        debug=os.getenv("DEBUG", False),
        log_level=os.getenv('LOG_LEVEL', "info"),
        proxy_headers=True
    )
