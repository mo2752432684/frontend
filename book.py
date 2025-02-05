from fastapi import FastAPI
from db import engine, Base
from routers import users, comments, posts

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(comments.router)
app.include_router(posts.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)