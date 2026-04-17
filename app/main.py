from fastapi import FastAPI

app = FastAPI(title="CI/CD Demo App")


@app.get("/")
def read_root():
    return {"message": "Hello CI/CD"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/greet/{name}")
def greet(name: str):
    return {"greeting": f"Hello, {name}!"}
