from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.resume import create_random_resume


def test_create_resume(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}/resumes/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_resume(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    resume = create_random_resume(db)
    response = client.get(
        f"{settings.API_V1_STR}/resumes/{resume.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == resume.title
    assert content["description"] == resume.description
    assert content["id"] == resume.id
    assert content["owner_id"] == resume.owner_id


def test_read_resume_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/resumes/999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Resume not found"


def test_read_resume_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    resume = create_random_resume(db)
    response = client.get(
        f"{settings.API_V1_STR}/resumes/{resume.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_resumes(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_resume(db)
    create_random_resume(db)
    response = client.get(
        f"{settings.API_V1_STR}/resumes/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_resume(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    resume = create_random_resume(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/resumes/{resume.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == resume.id
    assert content["owner_id"] == resume.owner_id


def test_update_resume_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/resume/999",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Not Found"


def test_update_resume_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    resume = create_random_resume(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/resumes/{resume.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_resume(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    resume = create_random_resume(db)
    response = client.delete(
        f"{settings.API_V1_STR}/resumes/{resume.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Resume deleted successfully"


def test_delete_resume_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/resumes/999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Resume not found"


def test_delete_resume_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    resume = create_random_resume(db)
    response = client.delete(
        f"{settings.API_V1_STR}/resumes/{resume.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"
