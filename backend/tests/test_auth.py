import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

from main import app
from app.database import get_session  
from app.models import User  


test_sqlite_url = "sqlite:///:memory:"
test_engine = create_engine(
    test_sqlite_url, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool 
)


@pytest.fixture(name="session", scope="module", autouse=True)
def session_fixture():
    # Build the tables once inside the static memory pool
    SQLModel.metadata.create_all(test_engine)
    
    # Override the database session dependency dynamically
    def override_get_session():
        with Session(test_engine) as session:
            yield session
            
    app.dependency_overrides[get_session] = override_get_session
    
    yield  

    
    app.dependency_overrides.clear()


client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API Running"}

def test_user_registration_success():
    signup_data = {
        "username": "testdeveloper",
        "email": "developer@example.com",
        "password": "supersecurepassword123"
    }
    
    response = client.post("/register", json=signup_data)
    
    assert response.status_code in [200, 201]
    
    data = response.json()
    assert data["message"] == "User Registered Successfully!"
    assert "user_id" in data