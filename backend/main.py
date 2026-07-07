from fastapi import FastAPI
from sqlmodel import SQLModel,create_engine,Field,Session

class User(SQLModel,table=True):
    id: int | None = Field(default=None,primary_key=True)
    username: str = Field(unique=True,index=True)
    email : str = Field(unique=True)
    password : str 

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

#this talks to database
engine = create_engine(sqlite_url,connect_args={"check_same_thread" : False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI(title="ResearchMind")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message" : "API Running and Database Connected"}

