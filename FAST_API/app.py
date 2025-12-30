
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount the 'static' directory to serve CSS/JS/images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Tell FastAPI where your templates live
templates = Jinja2Templates(directory="templates")

# GET endpoint: render the HTML template
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    # Pass variables to your template via the 'context' dict
    ctx = {
        "request": request,      # required by FastAPI/Jinja2
        "title": "Welcome to FastAPI + Jinja2",
        "message": "Hello, MLOps Engineer! 👋",
    }
    return templates.TemplateResponse("index.html", ctx)

# Example POST endpoint: render template with form data
@app.post("/submit", response_class=HTMLResponse)
def submit_form(request: Request, name: str = Form(...)):
    ctx = {
        "request": request,
        "title": "Form Submitted",
        "message": f"Thanks, {name}! Your submission was received.",
    }
    return templates.TemplateResponse("index.html", ctx)
