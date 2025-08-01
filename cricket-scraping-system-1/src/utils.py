
import asyncio
import hashlib
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse
import psutil
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting utility"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make a request"""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        # Check if we can make a request
        if len(self.requests) >= self.max_requests:
            # Wait until we can make a request
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                return await self.acquire()
        
        # Record this request
        self.requests.append(now)

class ResourceMonitor:
    """Monitor system resources"""
    
    def __init__(self, max_memory_mb: int = 500, max_cpu_percent: int = 80):
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.max_cpu = max_cpu_percent
    
    def check_resources(self) -> Dict[str, Any]:
        """Check current resource usage"""
        process = psutil.Process()
        
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent()
        
        return {
            'memory_used': memory_info.rss,
            'memory_percent': (memory_info.rss / self.max_memory) * 100,
            'cpu_percent': cpu_percent,
            'is_memory_ok': memory_info.rss < self.max_memory,
            'is_cpu_ok': cpu_percent < self.max_cpu
        }
    
    def should_throttle(self) -> bool:
        """Determine if we should throttle operations"""
        resources = self.check_resources()
        return not (resources['is_memory_ok'] and resources['is_cpu_ok'])

class DataValidator:
    """Validate scraped data"""
    
    @staticmethod
    def validate_match_info(match_data: Dict[str, Any]) -> bool:
        """Validate match information"""
        required_fields = ['match_id', 'team1', 'team2', 'date']
        return all(field in match_data and match_data[field] for field in required_fields)
    
    @staticmethod
    def validate_score(score: str) -> bool:
        """Validate score format (e.g., '156/4', '89/10', '234/3*')"""
        if not score:
            return False
        
        # Remove any trailing indicators like '*' for declared innings
        clean_score = score.rstrip('*d ')
        
        # Check format: runs/wickets
        pattern = r'^\d+/\d+
        return bool(re.match(pattern, clean_score))
    
    @staticmethod
    def validate_overs(overs: str) -> bool:
        """Validate overs format (e.g., '20.0', '19.4', '50.0')"""
        if not overs:
            return False
        
        try:
            float(overs)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Clean and sanitize text data"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,():/]', '', text)
        
        return text.strip()

class CacheManager:
    """Simple in-memory cache for reducing redundant requests"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache = {}
        self.timestamps = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key not in self.cache:
            return None
        
        # Check if expired
        if time.time() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any):
        """Set item in cache"""
        # Clean up if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.timestamps.keys(), key=self.timestamps.get)
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()

def generate_unique_id(*args) -> str:
    """Generate unique identifier from arguments"""
    content = ''.join(str(arg) for arg in args)
    return hashlib.md5(content.encode()).hexdigest()[:12]

def parse_datetime(date_str: str, time_str: str = "") -> Optional[datetime]:
    """Parse date and time strings into datetime object"""
    formats_to_try = [
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M",
        "%Y/%m/%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%d %b %Y %H:%M",
        "%d %B %Y %H:%M",
        "%b %d, %Y %H:%M",
        "%B %d, %Y %H:%M"
    ]
    
    datetime_str = f"{date_str} {time_str}".strip()
    
    for fmt in formats_to_try:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse datetime: {datetime_str}")
    return None

def calculate_strike_rate(runs: int, balls: int) -> float:
    """Calculate strike rate"""
    if balls == 0:
        return 0.0
    return (runs / balls) * 100

def calculate_economy_rate(runs: int, overs: float) -> float:
    """Calculate bowling economy rate"""
    if overs == 0:
        return 0.0
    return runs / overs

def is_match_live(status: str) -> bool:
    """Check if match is currently live"""
    live_statuses = [
        'live', 'in progress', 'playing', 'ongoing',
        'innings break', 'tea', 'lunch', 'drinks'
    ]
    return status.lower() in live_statuses

def extract_numbers(text: str) -> List[int]:
    """Extract all numbers from text"""
    return [int(match) for match in re.findall(r'\d+', text)]

def clean_html(html_content: str) -> str:
    """Remove HTML tags and clean content"""
    # Remove script and style elements
    html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL)
    
    # Remove HTML tags
    html_content = re.sub(r'<[^>]+>', '', html_content)
    
    # Clean up whitespace
    html_content = ' '.join(html_content.split())
    
    return html_content

class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_network_error(error: Exception, url: str) -> bool:
        """Handle network-related errors, return True if should retry"""
        error_str = str(error).lower()
        
        # Temporary errors that should be retried
        retry_errors = [
            'timeout', 'connection', 'network', 'dns',
            'temporary failure', 'service unavailable'
        ]
        
        should_retry = any(err in error_str for err in retry_errors)
        
        if should_retry:
            logger.warning(f"Temporary network error for {url}: {error}")
        else:
            logger.error(f"Permanent network error for {url}: {error}")
        
        return should_retry
    
    @staticmethod
    def handle_parsing_error(error: Exception, content_type: str):
        """Handle content parsing errors"""
        logger.error(f"Parsing error for {content_type}: {error}")
        # Could implement fallback parsing methods here