import io

from fastapi.testclient import TestClient

from app.utils.upload import upload_rate_limiter

# Minimal 1x1 transparent PNG bytes
TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
    b"\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00"
    b"IEND\xaeB`\x82"
)

# Minimal JPEG header
TINY_JPEG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\xff\xd9"
)


def get_authenticated_user_headers(client: TestClient, username: str) -> dict[str, str]:
    payload = {"username": username, "password": "password123", "role": "user"}
    client.post("/api/auth/register", json=payload)
    login_res = client.post("/api/auth/login", json=payload)
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_valid_png_and_serve_static(client: TestClient):
    """Test uploading a valid PNG file and retrieving it via /uploads/<filename>."""
    upload_rate_limiter.reset()
    headers = get_authenticated_user_headers(client, "uploader_bob")

    files = {"file": ("dish.png", io.BytesIO(TINY_PNG), "image/png")}
    response = client.post("/api/upload/image", files=files, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "url" in data
    assert data["url"].startswith("/uploads/")
    assert data["url"].endswith(".png")
    assert data["size"] == len(TINY_PNG)

    # Verify that the image is served by FastAPI StaticFiles
    serve_res = client.get(data["url"])
    assert serve_res.status_code == 200
    assert serve_res.content == TINY_PNG


def test_upload_valid_jpeg(client: TestClient):
    """Test uploading a valid JPEG file."""
    upload_rate_limiter.reset()
    headers = get_authenticated_user_headers(client, "uploader_alice")

    files = {"file": ("soup.jpg", io.BytesIO(TINY_JPEG), "image/jpeg")}
    response = client.post("/api/upload/image", files=files, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["url"].endswith(".jpg")


def test_upload_unauthenticated_rejected(client: TestClient):
    """Test that anonymous users cannot upload files."""
    files = {"file": ("test.png", io.BytesIO(TINY_PNG), "image/png")}
    response = client.post("/api/upload/image", files=files)
    assert response.status_code == 401


def test_upload_fake_image_magic_bytes_rejected(client: TestClient):
    """Test that a non-image file disguised with .png extension is rejected."""
    upload_rate_limiter.reset()
    headers = get_authenticated_user_headers(client, "uploader_hacker")

    fake_content = b"<?php echo 'malicious script'; ?>"
    files = {"file": ("malware.png", io.BytesIO(fake_content), "image/png")}
    response = client.post("/api/upload/image", files=files, headers=headers)
    assert response.status_code == 400
    assert "не является валидным изображением" in response.json()["detail"]


def test_upload_invalid_extension_rejected(client: TestClient):
    """Test that forbidden extensions are rejected immediately."""
    upload_rate_limiter.reset()
    headers = get_authenticated_user_headers(client, "uploader_dan")

    files = {"file": ("payload.exe", io.BytesIO(TINY_PNG), "application/octet-stream")}
    response = client.post("/api/upload/image", files=files, headers=headers)
    assert response.status_code == 400
    assert "Недопустимое расширение" in response.json()["detail"]


def test_upload_oversized_file_rejected(client: TestClient):
    """Test that files exceeding 5 MB are rejected with 413."""
    upload_rate_limiter.reset()
    headers = get_authenticated_user_headers(client, "uploader_eve")

    # Generate 5.2 MB payload with valid PNG header
    oversized_data = b"\x89PNG\r\n\x1a\n" + b"X" * (5 * 1024 * 1024 + 200 * 1024)
    files = {"file": ("huge_dish.png", io.BytesIO(oversized_data), "image/png")}
    response = client.post("/api/upload/image", files=files, headers=headers)
    assert response.status_code == 413
    assert "превышает лимит 5 МБ" in response.json()["detail"]


def test_upload_rate_limit(client: TestClient):
    """Test that users cannot spam upload more than 10 images per minute."""
    upload_rate_limiter.reset()
    headers = get_authenticated_user_headers(client, "uploader_spammer")

    # 10 successful uploads
    for _ in range(10):
        files = {"file": ("spam.png", io.BytesIO(TINY_PNG), "image/png")}
        res = client.post("/api/upload/image", files=files, headers=headers)
        assert res.status_code == 201

    # 11th upload should trigger 429
    files = {"file": ("spam.png", io.BytesIO(TINY_PNG), "image/png")}
    blocked_res = client.post("/api/upload/image", files=files, headers=headers)
    assert blocked_res.status_code == 429
    assert "Превышен лимит загрузок" in blocked_res.json()["detail"]

    # Cleanup rate limiter
    upload_rate_limiter.reset()
