from slowapi import Limiter
from app.client_ip import client_ip
limiter = Limiter(key_func=client_ip, default_limits=["100/15minutes"])
