from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
# Disable default global limits; apply per-route if needed
limiter = Limiter(key_func=get_remote_address, default_limits=[]) 

