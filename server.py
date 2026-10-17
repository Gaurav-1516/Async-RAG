import os
import shutil
import tempfile
from fastapi import FastAPI, Query, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .client.rq_client import queue
from .queues.worker import process_query, process_file

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get('/', response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post('/upload')
def upload_file(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1] if file.filename else ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name
        
        # Synchronous processing instead of queue
        result = process_file(temp_path)
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@app.post('/chat')
def chat(query: str = Query(..., description="The chat query of user")):
    job = queue.enqueue(process_query, query)
    return {"status":"queued", "job_id": job.id}

@app.get('/job-status')
def get_result(job_id: str):
    job = queue.fetch_job(job_id=job_id)
    result = job.result if job else None

    return {"result":result}