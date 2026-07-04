from fastapi import FastAPI

app = FastAPI(title="Veridict Backend")

@app.get("/")
def read_root():
    return {"message": "Veridict backend is running"}
