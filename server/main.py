from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def healthcheck():
  return {
    "message": "All systems operational."
  }