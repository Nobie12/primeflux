from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse

from core.core_functions.services.cache.redis_client import RedisClient


def health_check(request, *args, **kwargs):
    """
    System health check endpoint.
    Returns 200 OK if all backend systems are healthy,
    and 503 Service Unavailable if any dependency fails.
    """
    health_status = {
        "status": "healthy",
        "services": {"application": "online", "database": "unhealthy", "redis": "unhealthy"},
    }

    # 1. Test PostgreSQL Connection
    db_conn = connections["default"]
    try:
        # Forces a minimal query round-trip to the DB engine
        db_conn.cursor()
        health_status["services"]["database"] = "online"
    except OperationalError:
        health_status["status"] = "unhealthy"

    # 2. Test Redis Connection
    redis_service = RedisClient()
    if redis_service.ping():
        health_status["services"]["redis"] = "online"
    else:
        health_status["status"] = "unhealthy"

    # Determine standard REST status code response
    status_code = 200 if health_status["status"] == "healthy" else 503

    return JsonResponse(health_status, status=status_code)
