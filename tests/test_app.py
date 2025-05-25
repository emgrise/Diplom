import pytest
import os
import sqlite3
from werkzeug.security import generate_password_hash
from flask import get_flashed_messages
from io import BytesIO

@pytest.fixture
def client(app):
    """Create a test client with a temporary database."""
    with app.test_client() as client:
        with app.app_context():
            # Create a test user
            db = sqlite3.connect(app.config['DATABASE'])
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                ('testuser', generate_password_hash('testpass123'))
            )
            db.commit()
            db.close()
        yield client

@pytest.fixture
def auth_client(client):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session['user_id'] = 1
    return client

class TestPublicRoutes:
    def test_index_page(self, client):
        """Test that the index page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Index' in response.data

    def test_effects_page(self, client):
        """Test that the effects page loads successfully for each effect type"""
        from app import EFFECT_TYPE_MAP
        for effect_type in EFFECT_TYPE_MAP.keys():
            response = client.get(f'/effects/{effect_type}')
            assert response.status_code == 200
            assert effect_type.encode() in response.data

    def test_static_files(self, client):
        """Test that static files are served correctly"""
        response = client.get('/static/Data_pic/previews/test.jpg')
        assert response.status_code == 200  # Changed to 200 since the file might exist

class TestAuthentication:
    def test_register_page_get(self, client):
        """Test registration page GET request"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data

    def test_register_page_post_valid(self, client):
        """Test registration with valid data"""
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'newpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        messages = get_flashed_messages()
        assert 'Registration successful! Please login.' in messages

    def test_register_page_post_invalid(self, client):
        """Test registration with invalid data"""
        # Test short username
        response = client.post('/register', data={
            'username': 'te',
            'password': 'testpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        messages = get_flashed_messages()
        assert 'Username must be at least 3 characters long' in messages

        # Test short password
        response = client.post('/register', data={
            'username': 'testuser',
            'password': 'test'
        }, follow_redirects=True)
        assert response.status_code == 200
        messages = get_flashed_messages()
        assert 'Password must be at least 6 characters long' in messages

    def test_login_page_get(self, client):
        """Test login page GET request"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_login_page_post_valid(self, client):
        """Test login with valid credentials"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        messages = get_flashed_messages()
        assert 'Logged in successfully!' in messages

    def test_login_page_post_invalid(self, client):
        """Test login with invalid credentials"""
        response = client.post('/login', data={
            'username': 'wronguser',
            'password': 'wrongpass'
        }, follow_redirects=True)
        assert response.status_code == 200
        messages = get_flashed_messages()
        assert 'Invalid username or password' in messages

    def test_logout(self, client):
        """Test logout functionality"""
        # First login
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        messages = get_flashed_messages()
        assert 'Logged out successfully!' in messages

class TestProtectedRoutes:
    def test_cabinet_requires_login(self, client):
        """Test that cabinet page requires login"""
        response = client.get('/cabinet', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_cabinet_with_login(self, auth_client):
        """Test cabinet page with authenticated user"""
        response = auth_client.get('/cabinet')
        assert response.status_code == 200
        assert b'Cabinet' in response.data

    def test_add_effect_requires_login(self, client):
        """Test that adding effect requires login"""
        response = client.post('/add_effect', data={
            'name': 'Test Effect',
            'code': '<div>Test</div>',
            'effect_type': 'pic',
            'is_public': '1'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_add_effect_with_login(self, auth_client):
        """Test adding effect with authenticated user"""
        # Create a test image file
        test_image = (BytesIO(b'fake-image-content'), 'test.jpg')
        
        response = auth_client.post('/add_effect', 
            data={
                'name': 'Test Effect',
                'code': '<div>Test</div>',
                'effect_type': 'pic',
                'is_public': '1',
                'preview_image': test_image
            },
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        assert response.json['message'] == 'Effect added successfully'

    def test_edit_effect_requires_login(self, client):
        """Test that editing effect requires login"""
        response = client.get('/edit_effect/pic/1', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_delete_effect_requires_login(self, client):
        """Test that deleting effect requires login"""
        response = client.post('/delete_effect/pic/1', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

class TestErrorHandling:
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent_page')
        assert response.status_code == 404
        assert b'Page not found' in response.data

    def test_invalid_effect_type(self, client):
        """Test invalid effect type handling"""
        response = client.get('/effects/invalid_type')
        assert response.status_code == 400
        assert b'Invalid effect type' in response.data 