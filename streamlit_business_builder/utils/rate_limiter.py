import time
from datetime import datetime, timedelta
import json
from typing import Optional, Tuple

class RateLimiter:
    def __init__(self):
        self.attempts = {}
        self.lockouts = {}
        
    def is_locked_out(self, username: str) -> Tuple[bool, Optional[int]]:
        """Check if a user is locked out"""
        if username in self.lockouts:
            lockout_time = self.lockouts[username]
            if datetime.now() < lockout_time:
                remaining = int((lockout_time - datetime.now()).total_seconds())
                return True, remaining
            else:
                del self.lockouts[username]
                if username in self.attempts:
                    del self.attempts[username]
        return False, None

    def record_attempt(self, username: str) -> Tuple[bool, Optional[int]]:
        """Record a failed login attempt"""
        now = datetime.now()
        
        if username not in self.attempts:
            self.attempts[username] = []
            
        # Clean old attempts
        self.attempts[username] = [
            attempt for attempt in self.attempts[username]
            if attempt > now - timedelta(minutes=5)
        ]
        
        self.attempts[username].append(now)
        
        # If more than 5 attempts in 5 minutes, lock out for 15 minutes
        if len(self.attempts[username]) >= 5:
            self.lockouts[username] = now + timedelta(minutes=15)
            return True, 15
            
        return False, None 