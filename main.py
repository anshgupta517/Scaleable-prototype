from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello from your scalable FastAPI app!"}

# Define another simple endpoint
@app.get("/items/{item_id}")
async def read_item(item_id: int, query_param: str | None = None):
    item_data = {"item_id": item_id}
    if query_param:
        item_data["query_param"] = query_param
    return item_data