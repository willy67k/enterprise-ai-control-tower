from fastapi import FastAPI

app = FastAPI(title="Enterprise AI Control Tower")


@app.get("/")
def read_root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7801)
