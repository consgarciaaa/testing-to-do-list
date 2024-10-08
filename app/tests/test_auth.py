

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_password_hashing(client):
    # Setup: Create a new user and hash their password
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    # Verify that the password is hashed
    assert user.password_hash is not None
    assert check_password_hash(user.password_hash, 'password123')

def test_login_valid_credentials(client):
    # Setup: Create a user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Test: Log in with valid credentials
    response = client.post(url_for('auth.login'), data={'username': 'testuser', 'password': 'password123'})
    assert response.status_code == 302  # Redirect to the task page after successful login

def test_login_invalid_credentials(client):
    # Setup: Create a user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Test: Log in with an incorrect password
    response = client.post(url_for('auth.login'), data={'username': 'testuser', 'password': 'wrongpassword'})
    assert b'Invalid username or password' in response.data  # Flash message for invalid credentials

def test_session_management(client):
    # Setup: Create a user and log in
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Log in
    client.post(url_for('auth.login'), data={'username': 'testuser', 'password': 'password123'})
    
    # Test: Check session exists (e.g., by accessing a login-required page)
    response = client.get(url_for('tasks.index'))
    assert response.status_code == 200  # Should succeed because the user is logged in
    
    # Test: Log out
    client.get(url_for('auth.logout'))
    
    # Try accessing a login-required page after logout
    response = client.get(url_for('tasks.index'))
    assert response.status_code == 302  # Should redirect to login page since the session ended

def test_oauth_login(client):
    # Setup: OAuth login test using a mock provider
    # This would typically use a library like `responses` to mock the OAuth process
    
    # Test: Simulate OAuth login callback
    response = client.get(url_for('auth.oauth_callback', provider='google'))
    assert response.status_code == 302  # Assuming it redirects to task page after successful OAuth login

    # You can extend this to mock OAuth responses and check how your app handles them.
