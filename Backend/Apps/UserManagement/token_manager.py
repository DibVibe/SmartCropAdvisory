import secrets
import logging
from typing import Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)


class TokenManager:
    """Enhanced token manager with proper Redis integration"""

    def __init__(self):
        self.redis_available = getattr(settings, "REDIS_AVAILABLE", False)
        self.cache = caches["tokens"] if "tokens" in caches else caches["default"]
        self.token_expiry = getattr(settings, "REDIS_TOKEN_EXPIRY", 604800)  # 7 days
        self.token_prefix = getattr(settings, "REDIS_TOKEN_PREFIX", "auth_token")

        if self.redis_available:
            try:
                import redis

                self.redis_client = redis.Redis(
                    host=getattr(settings, "REDIS_HOST", "localhost"),
                    port=getattr(settings, "REDIS_PORT", 6379),
                    db=getattr(settings, "REDIS_TOKEN_DB", 2),
                    password=getattr(settings, "REDIS_PASSWORD", None),
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )
                # Test connection
                self.redis_client.ping()
                logger.info("✅ TokenManager using Redis for token storage")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed, using cache fallback: {e}")
                self.redis_client = None
                self.redis_available = False
        else:
            self.redis_client = None
            logger.info("✅ TokenManager using cache fallback for token storage")

    def generate_token(self) -> str:
        """Generate a secure random token"""
        return secrets.token_hex(32)  # 64 character token

    def store_token(self, token: str, user_id: str, expiry_hours: int = None) -> bool:
        """Store token with user ID"""
        try:
            expiry = expiry_hours or (self.token_expiry // 3600)
            key = f"{self.token_prefix}:{token}"

            if self.redis_client:
                # Use Redis directly for better control
                result = self.redis_client.setex(key, expiry * 3600, user_id)
                return bool(result)
            else:
                # Use Django cache
                self.cache.set(key, user_id, expiry * 3600)
                return True

        except Exception as e:
            logger.error(f"Failed to store token: {e}")
            return False

    def get_user_id_by_token(self, token: str) -> Optional[str]:
        """Get user ID by token"""
        try:
            key = f"{self.token_prefix}:{token}"

            if self.redis_client:
                user_id = self.redis_client.get(key)
            else:
                user_id = self.cache.get(key)

            return user_id

        except Exception as e:
            logger.error(f"Failed to get user by token: {e}")
            return None

    def delete_token(self, token: str) -> bool:
        """Delete/invalidate token"""
        try:
            key = f"{self.token_prefix}:{token}"

            if self.redis_client:
                result = self.redis_client.delete(key)
                return bool(result)
            else:
                self.cache.delete(key)
                return True

        except Exception as e:
            logger.error(f"Failed to delete token: {e}")
            return False

    def refresh_token_expiry(self, token: str, expiry_hours: int = None) -> bool:
        """Refresh token expiry"""
        try:
            user_id = self.get_user_id_by_token(token)
            if user_id:
                return self.store_token(token, user_id, expiry_hours)
            return False

        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return False

    def get_token_info(self, token: str) -> dict:
        """Get token information including TTL"""
        try:
            key = f"{self.token_prefix}:{token}"
            user_id = self.get_user_id_by_token(token)

            if not user_id:
                return {"valid": False}

            ttl = None
            if self.redis_client:
                ttl = self.redis_client.ttl(key)

            return {
                "valid": True,
                "user_id": user_id,
                "ttl_seconds": ttl,
                "expires_in": ttl if ttl and ttl > 0 else None,
            }

        except Exception as e:
            logger.error(f"Failed to get token info: {e}")
            return {"valid": False, "error": str(e)}

    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens (Redis handles this automatically)"""
        if not self.redis_client:
            return 0

        try:
            # Redis automatically removes expired keys
            # This method is for manual cleanup if needed
            pattern = f"{self.token_prefix}:*"
            keys = self.redis_client.keys(pattern)
            expired_count = 0

            for key in keys:
                ttl = self.redis_client.ttl(key)
                if ttl == -2:  # Key doesn't exist (expired)
                    expired_count += 1

            return expired_count

        except Exception as e:
            logger.error(f"Failed to cleanup tokens: {e}")
            return 0


# Global token manager instance
token_manager = TokenManager()
