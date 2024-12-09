from datetime import UTC
from datetime import datetime
from datetime import timedelta

import jwt
from django.conf import settings


def generate_email_token(user):
    payload = {
        "user_id": user.id,
        "exp": datetime.now(tz=UTC) + timedelta(minutes=30),
        "iat": datetime.now(tz=UTC),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
