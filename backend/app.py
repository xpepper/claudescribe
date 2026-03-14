from fastapi import FastAPI

app = FastAPI(title="Claudescribe")

@app.get("/api/health")
def health():
    return {"status": "ok"}
