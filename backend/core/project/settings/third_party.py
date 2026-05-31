from datetime import timedelta

# JWT SETUP
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # 5 mins is short for dev, maybe 60?
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "core.apps.accounts.serializers.auth.TokenObtainPairSerializer",
}

# Redis setup
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
