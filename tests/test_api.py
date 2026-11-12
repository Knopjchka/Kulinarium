from fastapi.testclient import TestClient


def test_root_serves_web_ui(client: TestClient):
    """Test that GET / returns the Web UI."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Кулинариум" in response.text


def test_auth_registration_and_login(client: TestClient):
    """Test user registration, JWT generation, and profile lookup."""
    reg_payload = {
        "username": "chef_anton",
        "password": "secretpassword123",
        "role": "user",
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["username"] == "chef_anton"
    assert "password" not in user_data
    assert "password_hash" not in user_data

    # Duplicate username check
    dup_res = client.post("/api/auth/register", json=reg_payload)
    assert dup_res.status_code == 400

    # Login
    login_res = client.post(
        "/api/auth/login",
        json={"username": "chef_anton", "password": "secretpassword123"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token

    # Check /api/auth/me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "chef_anton"


def test_recipe_crud_and_relationships(client: TestClient):
    """Test creating, reading, updating, and deleting recipes with ingredients and steps."""
    # 1. Unauthenticated creation is rejected
    unauth_res = client.post("/api/recipes", json={"name": "Test"})
    assert unauth_res.status_code == 401

    # 2. Register regular user who CAN create recipes
    reg_user = {"username": "regular_cook", "password": "password123", "role": "user"}
    client.post("/api/auth/register", json=reg_user)
    u_res = client.post("/api/auth/login", json=reg_user)
    u_token = u_res.json()["access_token"]
    u_headers = {"Authorization": f"Bearer {u_token}"}

    recipe_payload = {
        "name": "Грибной крем-суп",
        "description": "Ароматный суп из белых грибов со сливками и зеленью.",
        "category": "Первые блюда",
        "subcategory": "супы",
        "image_path": "https://example.com/soup.jpg",
        "ingredients": [
            {"name": "Шампиньоны", "unit": {"name": "г", "quantity": 400}},
            {"name": "Сливки", "unit": {"name": "мл", "quantity": 200}},
            {"name": "Луковица", "unit": {"name": "шт", "quantity": 1}},
        ],
        "steps": [
            {"number": 1, "text": "Нарезать грибы и лук, обжарить на сковороде."},
            {"number": 2, "text": "Залить бульоном и варить 15 минут."},
            {"number": 3, "text": "Взбить блендером, влить сливки и подогреть."},
        ],
    }

    # Regular registered user creates recipe
    create_res = client.post("/api/recipes", json=recipe_payload, headers=u_headers)
    assert create_res.status_code == 201
    recipe = create_res.json()
    assert recipe["name"] == "Грибной крем-суп"
    assert recipe["category"] == "Первые блюда"
    assert recipe["subcategory"] == "супы"
    assert recipe["author_username"] == "regular_cook"
    assert len(recipe["ingredients"]) == 3
    assert len(recipe["steps"]) == 3
    recipe_id = recipe["id"]

    # 3. Read recipe by ID
    get_res = client.get(f"/api/recipes/{recipe_id}")
    assert get_res.status_code == 200
    recipe_detail = get_res.json()
    assert recipe_detail["name"] == "Грибной крем-суп"
    assert recipe_detail["ingredients"][0]["unit"]["quantity"] == 400

    # 4. Filter recipes by subcategory
    filter_res = client.get("/api/recipes?subcategory=супы")
    assert filter_res.status_code == 200
    items = filter_res.json()
    assert any(r["id"] == recipe_id for r in items)

    # 5. Search recipes by ingredient
    search_res = client.get("/api/recipes?search=Шампиньоны")
    assert search_res.status_code == 200
    search_items = search_res.json()
    assert any(r["id"] == recipe_id for r in search_items)

    # 6. Another regular user CANNOT update this recipe
    other_user = {"username": "stranger_cook", "password": "password123", "role": "user"}
    client.post("/api/auth/register", json=other_user)
    o_token = client.post("/api/auth/login", json=other_user).json()["access_token"]
    o_headers = {"Authorization": f"Bearer {o_token}"}

    forbidden_update = client.put(
        f"/api/recipes/{recipe_id}",
        json={"name": "Взломанный суп"},
        headers=o_headers,
    )
    assert forbidden_update.status_code == 403

    # 7. Author CAN update their own recipe
    update_res = client.put(
        f"/api/recipes/{recipe_id}",
        json={"name": "Нежный грибной крем-суп"},
        headers=u_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Нежный грибной крем-суп"

    # 8. Another regular user CANNOT delete this recipe
    forbidden_delete = client.delete(f"/api/recipes/{recipe_id}", headers=o_headers)
    assert forbidden_delete.status_code == 403

    # 9. Admin CAN delete any recipe
    admin_data = {"username": "recipe_admin", "password": "password123", "role": "admin"}
    client.post("/api/auth/register", json=admin_data)
    admin_token = client.post("/api/auth/login", json=admin_data).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    del_res = client.delete(f"/api/recipes/{recipe_id}", headers=admin_headers)
    assert del_res.status_code == 204

    # 10. Verify deletion
    verify_res = client.get(f"/api/recipes/{recipe_id}")
    assert verify_res.status_code == 404


def test_categories_endpoint(client: TestClient):
    """Test that /api/recipes/categories returns categories and subcategories."""
    res = client.get("/api/recipes/categories")
    assert res.status_code == 200
    data = res.json()
    assert "categories" in data
    assert "subcategories" in data
    assert "супы" in data["subcategories"]
    assert "напитки" in data["subcategories"]
    assert "каша" in data["subcategories"]


def test_favourites_flow(client: TestClient):
    """Test adding and removing recipes from user's favourites."""
    # 1. Register admin user to create recipe and test favourites
    user_data = {"username": "fav_user", "password": "password123", "role": "admin"}
    client.post("/api/auth/register", json=user_data)
    login_res = client.post("/api/auth/login", json=user_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create a recipe to favourite
    recipe_res = client.post(
        "/api/recipes",
        json={
            "name": "Ягодный смузи",
            "description": "Освежающий напиток из ягод и йогурта.",
            "category": "Напитки",
            "subcategory": "напитки",
            "ingredients": [{"name": "Клубника", "unit": {"name": "г", "quantity": 150}}],
            "steps": [{"number": 1, "text": "Взбить клубнику с йогуртом в блендере."}],
        },
        headers=headers,
    )
    recipe_id = recipe_res.json()["id"]

    # 3. Toggle favourite: Add
    fav_res = client.post(f"/api/recipes/{recipe_id}/favourite", headers=headers)
    assert fav_res.status_code == 200
    assert fav_res.json()["favourite"] is True

    # Check that recipe appears in /api/users/me/favourites
    my_favs = client.get("/api/users/me/favourites", headers=headers)
    assert my_favs.status_code == 200
    fav_ids = [r["id"] for r in my_favs.json()]
    assert recipe_id in fav_ids

    # 4. Toggle favourite: Remove
    unfav_res = client.post(f"/api/recipes/{recipe_id}/favourite", headers=headers)
    assert unfav_res.status_code == 200
    assert unfav_res.json()["favourite"] is False

    # Check removed from favourites
    my_favs_after = client.get("/api/users/me/favourites", headers=headers)
    assert my_favs_after.status_code == 200
    fav_ids_after = [r["id"] for r in my_favs_after.json()]
    assert recipe_id not in fav_ids_after


def test_ingredients_and_units_endpoints(client: TestClient):
    """Test standalone ingredients and units endpoints."""
    # Create unit
    u_res = client.post("/api/units", json={"name": "ч. л.", "quantity": 2.5})
    assert u_res.status_code == 201
    assert u_res.json()["name"] == "ч. л."

    # List units
    units_list = client.get("/api/units")
    assert units_list.status_code == 200
    assert len(units_list.json()) >= 1

    # Create ingredient
    ing_res = client.post(
        "/api/ingredients",
        json={"name": "Корица", "unit": {"name": "ч. л.", "quantity": 1}},
    )
    assert ing_res.status_code == 201
    assert ing_res.json()["name"] == "Корица"

    # List ingredients
    ings_list = client.get("/api/ingredients?search=Корица")
    assert ings_list.status_code == 200
    assert len(ings_list.json()) >= 1


def test_admin_access_control(client: TestClient):
    """Test role checking on /api/users."""
    # Regular user
    client.post(
        "/api/auth/register",
        json={"username": "user1", "password": "password123", "role": "user"},
    )
    u_token = client.post(
        "/api/auth/login", json={"username": "user1", "password": "password123"}
    ).json()["access_token"]

    # Admin user
    client.post(
        "/api/auth/register",
        json={"username": "admin1", "password": "password123", "role": "admin"},
    )
    a_token = client.post(
        "/api/auth/login", json={"username": "admin1", "password": "password123"}
    ).json()["access_token"]

    # User denied
    res_user = client.get("/api/users", headers={"Authorization": f"Bearer {u_token}"})
    assert res_user.status_code == 403

    # Admin allowed
    res_admin = client.get("/api/users", headers={"Authorization": f"Bearer {a_token}"})
    assert res_admin.status_code == 200
    assert len(res_admin.json()) >= 2


def test_category_hierarchy_and_roles(client: TestClient):
    """Test that Category self-referential hierarchy and Role entities function properly."""
    # Register admin and login
    client.post(
        "/api/auth/register",
        json={"username": "hier_admin", "password": "password123", "role": "admin"},
    )
    token = client.post(
        "/api/auth/login", json={"username": "hier_admin", "password": "password123"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create recipe with hierarchical category and subcategory
    payload = {
        "name": "Том Ям с креветками",
        "description": "Острый тайский суп на кокосовом молоке.",
        "category": "Азиатская кухня",
        "subcategory": "супы",
        "ingredients": [{"name": "Креветки", "unit": {"name": "г", "quantity": 300}}],
        "steps": [{"number": 1, "text": "Сварить бульон с пастой том ям."}],
    }
    create_res = client.post("/api/recipes", json=payload, headers=headers)
    assert create_res.status_code == 201

    # Check categories endpoint returns new root and sub categories
    cats_res = client.get("/api/recipes/categories")
    assert cats_res.status_code == 200
    data = cats_res.json()
    assert "Азиатская кухня" in data["categories"]
    assert "супы" in data["subcategories"]


def test_unified_search_scoring(client: TestClient):
    """Test unified search ranking across name, category, ingredients, and description."""
    user_data = {"username": "search_master", "password": "password123", "role": "user"}
    client.post("/api/auth/register", json=user_data)
    token = client.post("/api/auth/login", json=user_data).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Exact name match: "Тирамису"
    client.post(
        "/api/recipes",
        json={
            "name": "Тирамису",
            "description": "Итальянский десерт с маскарпоне.",
            "category": "Десерты",
            "ingredients": [{"name": "Савоярди", "unit": {"name": "г", "quantity": 200}}],
            "steps": [{"number": 1, "text": "Собрать слоями десерт."}],
        },
        headers=headers,
    )

    # 2. Ingredient match for "Тирамису": recipe with ingredient "Печенье для тирамису"
    client.post(
        "/api/recipes",
        json={
            "name": "Кофейный трайфл",
            "description": "Быстрый слоеный десерт в стакане.",
            "category": "Десерты",
            "ingredients": [
                {"name": "Печенье для тирамису", "unit": {"name": "г", "quantity": 100}}
            ],
            "steps": [{"number": 1, "text": "Выложить слоями крем и печенье."}],
        },
        headers=headers,
    )

    # 3. Description match for "Тирамису": recipe with mention in description
    client.post(
        "/api/recipes",
        json={
            "name": "Крем маскарпоне",
            "description": "Воздушный крем, как в классическом тирамису дома.",
            "category": "Десерты",
            "ingredients": [{"name": "Маскарпоне", "unit": {"name": "г", "quantity": 250}}],
            "steps": [{"number": 1, "text": "Взбить маскарпоне со сливками."}],
        },
        headers=headers,
    )

    # Perform unified search for "тирамису"
    res = client.get("/api/recipes?search=тирамису")
    assert res.status_code == 200
    results = res.json()
    assert len(results) >= 3

    # Ranking check:
    # 1st place: exact name "Тирамису" (score 100)
    assert results[0]["name"] == "Тирамису"
    # 2nd place: ingredient match "Кофейный трайфл" (score 20)
    assert results[1]["name"] == "Кофейный трайфл"
    # 3rd place: description match "Крем маскарпоне" (score 10)
    assert results[2]["name"] == "Крем маскарпоне"


def test_comments_and_ratings(client: TestClient):
    """Test user comment posting, 0.5-step ratings, average calculation, and delete permissions."""
    # Register author user
    author = {"username": "baker_bob", "password": "password123", "role": "user"}
    client.post("/api/auth/register", json=author)
    bob_token = client.post("/api/auth/login", json=author).json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # Bob creates a recipe
    rec_res = client.post(
        "/api/recipes",
        json={
            "name": "Шарлотка с яблоками",
            "description": "Пышный бисквит с кислыми яблоками.",
            "category": "Выпечка",
            "ingredients": [{"name": "Яблоки", "unit": {"name": "шт", "quantity": 3}}],
            "steps": [{"number": 1, "text": "Нарезать яблоки и залить тестом."}],
        },
        headers=bob_headers,
    )
    assert rec_res.status_code == 201
    recipe_id = rec_res.json()["id"]

    # Register reviewer 1 (Alice)
    alice = {"username": "alice_critic", "password": "password123", "role": "user"}
    client.post("/api/auth/register", json=alice)
    alice_token = client.post("/api/auth/login", json=alice).json()["access_token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}

    # Alice posts comment with 4.5 rating (supports half star)
    c1_res = client.post(
        f"/api/recipes/{recipe_id}/comments",
        json={"rating": 4.5, "text": "Очень вкусно, но я добавила чуть меньше сахара."},
        headers=alice_headers,
    )
    assert c1_res.status_code == 201
    c1_data = c1_res.json()
    assert c1_data["rating"] == 4.5
    assert c1_data["username"] == "alice_critic"
    c1_id = c1_data["id"]

    # Verify recipe average rating is 4.5 and ratings_count is 1
    r_detail = client.get(f"/api/recipes/{recipe_id}").json()
    assert r_detail["rating"] == 4.5
    assert r_detail["ratings_count"] == 1

    # Register reviewer 2 (Charlie)
    charlie = {"username": "charlie_gourmet", "password": "password123", "role": "user"}
    client.post("/api/auth/register", json=charlie)
    charlie_token = client.post("/api/auth/login", json=charlie).json()["access_token"]
    charlie_headers = {"Authorization": f"Bearer {charlie_token}"}

    # Charlie rates 5.0
    c2_res = client.post(
        f"/api/recipes/{recipe_id}/comments",
        json={"rating": 5.0, "text": "Идеальная шарлотка! Рекомендую всем."},
        headers=charlie_headers,
    )
    assert c2_res.status_code == 201

    # Verify updated recipe rating: (4.5 + 5.0) / 2 = 4.75 -> rounded to 4.8
    r_detail2 = client.get(f"/api/recipes/{recipe_id}").json()
    assert r_detail2["rating"] == 4.8
    assert r_detail2["ratings_count"] == 2

    # Get comments list
    comments_res = client.get(f"/api/recipes/{recipe_id}/comments")
    assert comments_res.status_code == 200
    comments_list = comments_res.json()
    assert len(comments_list) == 2
    # Ordered by newest first
    assert comments_list[0]["username"] == "charlie_gourmet"
    assert comments_list[1]["username"] == "alice_critic"

    # Bob (recipe author, but not comment author) tries to delete Alice's comment -> 403
    bob_del_res = client.delete(f"/api/recipes/{recipe_id}/comments/{c1_id}", headers=bob_headers)
    assert bob_del_res.status_code == 403

    # Alice deletes her own comment -> 204
    alice_del_res = client.delete(
        f"/api/recipes/{recipe_id}/comments/{c1_id}",
        headers=alice_headers,
    )
    assert alice_del_res.status_code == 204

    # Alice's comment is gone
    comments_after = client.get(f"/api/recipes/{recipe_id}/comments").json()
    assert len(comments_after) == 1
    assert comments_after[0]["id"] != c1_id
