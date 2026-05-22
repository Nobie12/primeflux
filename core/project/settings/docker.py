if IN_DOCKER:
    print("Running in Docker, applying Docker-specific settings...")
    assert MIDDLEWARE[:1] == [
        'django.middleware.security.SecurityMiddleware',
    ]