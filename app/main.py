import aioredis
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


async def init_redis():
    redis = await aioredis.from_url(
        'redis://@88.198.16.68:6379', password="b3e8oLd2t81"
    )
    return redis

@app.on_event('startup')
async def create_redis():
    app.state.redis = await init_redis()

@app.on_event('shutdown')
async def close_redis():
    await app.state.redis.close()

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/form', response_class=HTMLResponse)
async def index(request: Request, first_name: str = Form(...), last_name: str = Form(...)):
    # TODO: email?
    redis = request.app.state.redis
    full_name = f"{first_name}_{last_name}".lower()
    is_old_user = await redis.sismember('users', full_name)
    if not is_old_user:
        message = f"{first_name.capitalize()} {last_name.capitalize()}, you are welcomed! \U0001F60D"
        await redis.sadd('users', full_name)
    else:
        message = f"Glad to see you again, {first_name.capitalize()} \U0001F929"
    return templates.TemplateResponse('user.html', {'request': request, 'message': message})

@app.get('/users', response_class=HTMLResponse)
async def users(request: Request):
    redis = request.app.state.redis
    _users_list = await redis.smembers('users')
    users_list = []
    for user in _users_list:
        first_name = user.decode('utf-8').split('_')[0].capitalize()
        last_name = user.decode('utf-8').split('_')[1].capitalize()
        users_list.append(f"{first_name} {last_name}")
    return templates.TemplateResponse('users.html', {'request': request, 'users': users_list})