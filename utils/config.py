import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the Bangladesh AI Agent"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    BING_API_KEY = os.getenv("BING_API_KEY")
    
    # Database paths
    INSTITUTIONS_DB = "data/institutions.db"
    HOSPITALS_DB = "data/hospitals.db"
    RESTAURANTS_DB = "data/restaurants.db"
    
    # Cache settings
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour default
    CACHE_DB = os.getenv('CACHE_DB', 'cache/query_cache.db')
    REDIS_URL = os.getenv("REDIS_URL")
    
    # Logging
    LOG_FILE = "logs/queries.log"
    LOG_LEVEL = "INFO"
    LOG_DB = os.getenv('LOG_DB', 'logs/query_log.db')
    
    # Agent settings
    MAX_RETRIES = 2
    RESPONSE_TIMEOUT = 30  # seconds
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ["OPENAI_API_KEY"]
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
        
        # Check if at least one search API key is available
        search_keys = ["TAVILY_API_KEY", "SERPAPI_API_KEY", "BING_API_KEY"]
        if not any(getattr(cls, key) for key in search_keys):
            raise ValueError("At least one search API key (TAVILY_API_KEY, SERPAPI_API_KEY, or BING_API_KEY) is required")
