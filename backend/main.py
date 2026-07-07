from fastapi import FastAPI,HTTPException,Depends,status
from sqlmodel import SQLModel,create_engine,Field,Session,select
from pydantic import EmailStr
from datetime import datetime,timedelta,timezone
import bcrypt
import jwt

SECRET_KEY = "my_super_secret_key_for_researchmind_ai"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_tokens(data : dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp" : expire})

    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    # Convert plain text to bytes, salt it, and hash it
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8') # Convert back to a clean text string for the DB

def verify_password(plain_password : str , hashed_password : str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


class User(SQLModel,table=True):
    id: int | None = Field(default=None,primary_key=True)
    username: str = Field(unique=True,index=True)
    email : str = Field(unique=True)
    hashed_password : str 

class UserCreate(SQLModel): #this helps to user enter these things
    username: str
    email: EmailStr
    password: str

class UserLogin(SQLModel):
    username : str
    password : str

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

#this talks to database
engine = create_engine(sqlite_url,connect_args={"check_same_thread" : False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():  #to open and close DB
    with Session(engine) as session:
        yield session

app = FastAPI(title="ResearchMind")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message" : "API Running and Database Connected"}

@app.post("/register")
def register(user_data : UserCreate, session : Session = Depends(get_session)):
    #1. check if username already exists
    existing_user = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="Username already exists")
    #2. check if email already exists
    existing_email = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_email:
        raise HTTPException(status_code=400,detail="Email already exists")
    
    secured_hash_password = get_password_hash(user_data.password)

    new_user = User(
        username=user_data.username,
        email = user_data.email,
        hashed_password = secured_hash_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message" : "User Registered Successfully!" , "user_id" : new_user.id}

@app.post("/login")
def login(login_data : UserLogin, session : Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == login_data.username)).first()

    if not user:
        raise HTTPException(
            status_code= status.HTTP_404_UNAUTHORIZED,
            detail= "Invalid username or password"
        )
    elif not verify_password(login_data.password,user.hashed_password):
        raise HTTPException(
            status_code= 401,
            detail= "Invalid username or password"
        )
    
    access_token = create_access_tokens(data = {"sub" : user.username})
    
    return {
        "access_token" : access_token,
        "token_type" : "bearer",
        "username" : user.username
    }



