import pytest
import bcrypt
from unittest.mock import MagicMock
 
from auth.auth_util import (
    hash_password,
    check_password,
    is_valid_email,
    is_valid_password,
    load_users,
    save_user,
    authenticate_user,
    update_last_login,
)
 

def test_hash_password_generates_valid_hash():
    pwd = "TestPassword123"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert bcrypt.checkpw(pwd.encode(), hashed.encode())
 
 
def test_check_password_valid():
    pwd = "StrongPass123"
    hashed = hash_password(pwd)
    assert check_password(pwd, hashed) is True
 
 
def test_check_password_invalid():
    pwd = "StrongPass123"
    hashed = hash_password(pwd)
    assert check_password("WrongPassword", hashed) is False
 

 
def test_is_valid_email():
    assert is_valid_email("test@example.com")
    assert not is_valid_email("invalid-email")
    assert not is_valid_email("@nope.com")
 
 
def test_is_valid_password():
    assert is_valid_password("Abcd1234")              # Valid
    assert not is_valid_password("abcdefg")           # Missing caps + number
    assert not is_valid_password("ABCDEFGH")          # Missing lowercase + number
    assert not is_valid_password("Abcdefgh")          # Missing number
    assert not is_valid_password("Abc12")             # Too short
 
 
@pytest.fixture
def mock_db(mocker):
    """Mock get_cursor() to avoid real DB."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch("auth.auth_util.get_cursor", return_value=(mock_conn, mock_cursor))
    return mock_conn, mock_cursor
 
 
def test_load_users(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        {"email": "one@test.com", "user_id": 1},
        {"email": "two@test.com", "user_id": 2},
    ]
 
    result = load_users()
 
    assert "one@test.com" in result
    assert "two@test.com" in result
    assert result["one@test.com"]["user_id"] == 1
 
 
 
def test_save_user_success(mock_db, mocker):
    mock_conn, mock_cursor = mock_db
 
    mock_cursor.lastrowid = 5
 
    mocker.patch("auth.auth_util.hash_password", return_value="hashed123")
 
    ok = save_user("John Doe", "john@test.com", "Abcd1234", "driver")
 
    assert ok is True
    assert mock_cursor.execute.call_count >= 2 
 
 
def test_save_user_duplicate_email(mock_db, mocker):
    mock_conn, mock_cursor = mock_db
 
    from pymysql import IntegrityError
    mock_cursor.execute.side_effect = IntegrityError("Duplicate email")
 
    ok = save_user("John Doe", "john@test.com", "Abcd1234", "driver")
 
    assert ok is False

 
def test_authenticate_user_success(mock_db, mocker):
    mock_conn, mock_cursor = mock_db
 
    fake_user = {
        "user_id": 1,
        "email": "test@test.com",
        "password": hash_password("Abcd1234"),
        "is_active": True,
        "role": "passenger",
    }
 
    mock_cursor.fetchone.return_value = fake_user
 
    mocker.patch("auth.auth_util.check_password", return_value=True)
    mocker.patch("auth.auth_util.update_last_login", return_value=None)
 
    user = authenticate_user("test@test.com", "Abcd1234")
 
    assert user is not None
    assert user["user_id"] == 1
 
 
def test_authenticate_user_invalid(mock_db, mocker):
    mock_conn, mock_cursor = mock_db
 
    mock_cursor.fetchone.return_value = None  
 
    user = authenticate_user("wrong@test.com", "Abcd1234")
 
    assert user is None

 
def test_update_last_login(mock_db):
    mock_conn, mock_cursor = mock_db
 
    update_last_login(5)
 
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()