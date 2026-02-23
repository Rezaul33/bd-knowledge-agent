# 🛠️ Development Guide

## 📋 Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Architecture](#project-architecture)
3. [Code Organization](#code-organization)
4. [Development Workflow](#development-workflow)
5. [Testing Guidelines](#testing-guidelines)
6. [Debugging and Troubleshooting](#debugging-and-troubleshooting)
7. [Performance Optimization](#performance-optimization)
8. [Security Best Practices](#security-best-practices)
9. [Deployment Guide](#deployment-guide)
10. [Contributing Guidelines](#contributing-guidelines)

## 🚀 Development Environment Setup

### Prerequisites

- **Python 3.8+** (recommended 3.9+)
- **Git** for version control
- **SQLite** for database management
- **Code Editor** (VS Code, PyCharm, or similar)

### Step-by-Step Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/Rezaul33/bd-knowledge-agent
cd bd-knowledge-agent
```

#### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda (optional)
conda create -n bd-agent python=3.9
conda activate bd-agent
```

#### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

#### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Required environment variables:
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for web search)
TAVILY_API_KEY=your_tavily_api_key
SERPAPI_API_KEY=your_serpapi_api_key
BING_API_KEY=your_bing_api_key

# Development settings
DEBUG=True
LOG_LEVEL=DEBUG
CACHE_ENABLED=True
```

#### 5. Initialize Databases

```bash
# Build databases with sample data
python scripts/build_databases.py --recreate --sample-data

# Or build without sample data
python scripts/build_databases.py --recreate
```

#### 6. Verify Installation

```bash
# Run comprehensive tests
python test_comprehensive.py

# Start the web interface
python run_streamlit.py

# Test CLI interface
python agent/main_agent.py --test
```

## 🏗️ Project Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Bangladesh Knowledge Agent                │
├─────────────────────────────────────────────────────────────┤
│  🎨 Streamlit Web Interface                                 │
│  ├── Chat Interface                                         │
│  ├── Session Management                                     │
│  └── Real-time Updates                                      │
├─────────────────────────────────────────────────────────────┤
│  🤖 Core Agent System                                       │
│  ├── Query Router (Intelligent Routing)                     │
│  ├── Tool Manager (Tool Orchestration)                      │
│  ├── Response Processor (Formatting & Cleaning)             │
│  └── Session Manager (State Management)                    │
├─────────────────────────────────────────────────────────────┤
│  🛠️ Tool Layer                                             │
│  ├── InstitutionsDBTool (Educational Institutions)          │
│  ├── HospitalsDBTool (Healthcare Facilities)               │
│  ├── RestaurantsDBTool (Food Service)                      │
│  └── WebSearchTool (General Knowledge)                      │
├─────────────────────────────────────────────────────────────┤
│  🔧 Utility Layer                                          │
│  ├── Cache Manager (SQLite Caching)                         │
│  ├── Query Logger (Analytics & Logging)                    │
│  ├── Confidence Scorer (Result Assessment)                  │
│  ├── Database Manager (SQLite Operations)                  │
│  └── Configuration Manager (Settings)                      │
├─────────────────────────────────────────────────────────────┤
│  💾 Data Layer                                             │
│  ├── Institutions Database (SQLite)                         │
│  ├── Hospitals Database (SQLite)                            │
│  ├── Restaurants Database (SQLite)                          │
│  ├── Cache Database (SQLite)                                │
│  └── Log Database (SQLite)                                  │
└─────────────────────────────────────────────────────────────┘
```

### Component Interactions

```python
# Query Flow Architecture
User Query → Streamlit UI → Main Agent → Query Router → Tool Selection → Tool Execution → Response Processing → Cache/Log → User Response
```

### Data Flow

1. **Input Processing**: User query received via web interface or CLI
2. **Query Analysis**: Query router analyzes and classifies the query
3. **Tool Selection**: Appropriate tool selected based on query type
4. **Execution**: Tool processes query and generates response
5. **Post-Processing**: Response formatted, confidence scored, metadata added
6. **Caching**: Result cached for future similar queries
7. **Logging**: Query metadata logged for analytics
8. **Response**: Final response returned to user

## 📁 Code Organization

### Directory Structure

```
bd-knowledge-agent/
├── 📂 agent/                    # Core agent logic
│   ├── main_agent.py           # Primary agent class
│   └── query_router.py         # Query routing logic
├── 📂 tools/                    # LangChain tools
│   ├── institutions_tool.py    # Institutions queries
│   ├── hospitals_tool.py       # Hospitals queries
│   ├── restaurants_tool.py     # Restaurants queries
│   └── web_search_tool.py      # Web search functionality
├── 📂 utils/                    # Utility modules
│   ├── config.py               # Configuration management
│   ├── database.py             # Database utilities
│   ├── cache_manager.py        # Caching system
│   ├── query_logger.py         # Logging system
│   └── confidence_scorer.py    # Confidence scoring
├── 📂 data/                     # Data storage
│   ├── institutions.db         # Institutions database
│   ├── hospitals.db            # Hospitals database
│   └── restaurants.db          # Restaurants database
├── 📂 cache/                    # Cache storage
├── 📂 logs/                     # Query logs
├── 📂 tests/                    # Test files
├── 📂 docs/                     # Documentation
├── 📂 scripts/                  # Utility scripts
├── streamlit_app.py           # Streamlit web interface
└── run_streamlit.py           # Streamlit launcher
```

### Code Standards

#### Python Style Guide

```python
# ✅ Good: Follow PEP 8
class BangladeshKnowledgeAgent:
    """Main agent class for Bangladesh Knowledge Agent."""
    
    def __init__(self, cache_enabled: bool = True) -> None:
        """Initialize the agent with optional caching."""
        self.cache_enabled = cache_enabled
        self.session_id = self._generate_session_id()
    
    def query(self, user_query: str, include_metadata: bool = False) -> Dict[str, Any]:
        """
        Process user query and return response.
        
        Args:
            user_query: The query string to process
            include_metadata: Whether to include metadata in response
            
        Returns:
            Dictionary containing response and optional metadata
        """
        # Implementation here
        pass

# ❌ Bad: Violates PEP 8
class bangladeshKnowledgeAgent:
    def __init__(self,cache_enabled=True):
        self.cache_enabled=cache_enabled
        self.session_id=self._generate_session_id()
```

#### Documentation Standards

```python
def calculate_confidence(
    self, 
    query: str, 
    tool_used: str, 
    sql_executed: bool, 
    fallback_used: bool, 
    result_empty: bool, 
    result: str
) -> float:
    """
    Calculate confidence score for query result.
    
    Args:
        query: Original user query string
        tool_used: Name of tool that processed the query
        sql_executed: Whether SQL query was successfully executed
        fallback_used: Whether fallback response was used
        result_empty: Whether the result is empty
        result: The actual result string
        
    Returns:
        Confidence score between 0.00 and 0.95
        
    Example:
        >>> agent = BangladeshKnowledgeAgent()
        >>> confidence = agent.calculate_confidence(
        ...     "How many universities in Dhaka?",
        ...     "InstitutionsDBTool",
        ...     True,
        ...     False,
        ...     False,
        ...     "Found 15 universities in Dhaka."
        ... )
        >>> print(confidence)
        0.92
    """
```

#### Error Handling Standards

```python
# ✅ Good: Comprehensive error handling
def _execute_query(self, sql: str) -> List[Dict[str, Any]]:
    """Execute SQL query with proper error handling."""
    try:
        conn = DatabaseManager.create_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        columns = [description[0] for description in cursor.description]
        result_list = [dict(zip(columns, row)) for row in results]
        
        return result_list
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

# ❌ Bad: No error handling
def _execute_query(self, sql: str):
    conn = DatabaseManager.create_connection(self.db_path)
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()
```

## 🔄 Development Workflow

### Git Workflow

#### 1. Branch Strategy

```bash
# Main branches
main          # Production-ready code
develop       # Integration branch
feature/*     # New features
bugfix/*      # Bug fixes
hotfix/*      # Critical fixes
release/*     # Release preparation
```

#### 2. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-tool-integration

# Make changes
# ... (development work) ...

# Commit changes
git add .
git commit -m "feat: Add new tool integration for universities"

# Push branch
git push origin feature/new-tool-integration

# Create pull request
# (through GitHub interface)
```

#### 3. Commit Message Standards

```bash
# Format: <type>(<scope>): <description>

# Types:
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Code style (formatting, etc.)
refactor: Code refactoring
test:     Tests
chore:    Maintenance tasks

# Examples:
feat(tools): Add new universities query tool
fix(router): Resolve query classification issue
docs(readme): Update installation instructions
style(agent): Format code according to PEP 8
refactor(cache): Improve caching performance
test(hospitals): Add comprehensive hospital tool tests
```

### Development Process

#### 1. Feature Development

```python
# Step 1: Design
# - Create feature design document
# - Define API interface
# - Plan implementation approach

# Step 2: Implementation
# - Write code following standards
# - Add comprehensive tests
# - Update documentation

# Step 3: Testing
# - Run unit tests
# - Run integration tests
# - Manual testing

# Step 4: Review
# - Code review by team
# - Documentation review
# - Performance testing

# Step 5: Deployment
# - Merge to develop branch
# - Test in staging environment
# - Deploy to production
```

#### 2. Debugging Process

```python
# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debug prints
def debug_query_processing(query: str):
    print(f"DEBUG: Processing query: {query}")
    classification = self.query_router.classify_query(query)
    print(f"DEBUG: Classification: {classification}")
    # ... continue debugging

# Use assert statements
def validate_response(response: Dict[str, Any]):
    assert 'success' in response, "Response missing 'success' key"
    assert 'response' in response, "Response missing 'response' key"
    assert isinstance(response['success'], bool), "success must be boolean"
```

## 🧪 Testing Guidelines

### Test Structure

#### 1. Unit Tests

```python
# tests/test_institutions_tool.py
import unittest
from tools.institutions_tool import InstitutionsDBTool

class TestInstitutionsDBTool(unittest.TestCase):
    """Test cases for InstitutionsDBTool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = InstitutionsDBTool()
    
    def test_university_count_query(self):
        """Test university count query"""
        result = self.tool._run("How many universities are in Dhaka?")
        self.assertIn("universities", result.lower())
        self.assertIn("dhaka", result.lower())
    
    def test_invalid_query(self):
        """Test invalid query handling"""
        result = self.tool._run("invalid query that doesn't match patterns")
        self.assertIn("couldn't understand", result.lower())
    
    def tearDown(self):
        """Clean up test fixtures"""
        pass
```

#### 2. Integration Tests

```python
# tests/test_integration.py
import unittest
from agent.main_agent import BangladeshKnowledgeAgent

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.agent = BangladeshKnowledgeAgent()
    
    def test_end_to_end_query_flow(self):
        """Test complete query processing flow"""
        response = self.agent.query("How many universities in Dhaka?")
        
        self.assertTrue(response['success'])
        self.assertIn('universities', response['response'])
        self.assertIn('dhaka', response['response'])
        
        if 'metadata' in response:
            self.assertIn('tool_used', response['metadata'])
            self.assertIn('confidence', response['metadata'])
```

#### 3. Performance Tests

```python
# tests/test_performance.py
import time
import unittest
from agent.main_agent import BangladeshKnowledgeAgent

class TestPerformance(unittest.TestCase):
    """Performance tests for the agent"""
    
    def setUp(self):
        self.agent = BangladeshKnowledgeAgent()
    
    def test_query_response_time(self):
        """Test query response time is within acceptable limits"""
        start_time = time.time()
        response = self.agent.query("How many universities in Dhaka?")
        execution_time = time.time() - start_time
        
        self.assertLess(execution_time, 2.0, "Query took too long to execute")
        self.assertTrue(response['success'])
    
    def test_cache_performance(self):
        """Test cache improves performance"""
        query = "How many universities in Dhaka?"
        
        # First query (no cache)
        start_time = time.time()
        self.agent.query(query)
        first_time = time.time() - start_time
        
        # Second query (cached)
        start_time = time.time()
        response = self.agent.query(query)
        second_time = time.time() - start_time
        
        self.assertLess(second_time, first_time, "Cache should improve performance")
        self.assertTrue(response['metadata']['cached'])
```

### Test Execution

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_institutions_tool.py

# Run with coverage
python -m pytest tests/ --cov=agent --cov=tools --cov=utils

# Run performance tests
python -m pytest tests/test_performance.py -v

# Generate coverage report
python -m pytest tests/ --cov=agent --cov-report=html
```

### Test Data Management

```python
# tests/conftest.py
import pytest
import sqlite3
import tempfile
import os

@pytest.fixture
def test_database():
    """Create temporary test database"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    # Create test database schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE institutions (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            location TEXT NOT NULL
        )
    ''')
    
    # Insert test data
    cursor.execute('''
        INSERT INTO institutions (name, type, location)
        VALUES ('Test University', 'University', 'Test City')
    ''')
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    os.unlink(db_path)
```

## 🐛 Debugging and Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Issues

```python
# Problem: SQLite database locked
# Solution: Use proper connection management

class DatabaseManager:
    @staticmethod
    def create_connection(db_path: str) -> sqlite3.Connection:
        """Create database connection with proper error handling"""
        try:
            conn = sqlite3.connect(db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
```

#### 2. Memory Issues

```python
# Problem: Memory leaks in long-running processes
# Solution: Proper resource cleanup

class CacheManager:
    def __init__(self):
        self._connections = []
    
    def __del__(self):
        """Cleanup connections on object destruction"""
        for conn in self._connections:
            try:
                conn.close()
            except:
                pass
```

#### 3. Performance Issues

```python
# Problem: Slow query performance
# Solution: Database indexing and query optimization

def optimize_database():
    """Add indexes for better performance"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_institutions_name ON institutions(name)",
        "CREATE INDEX IF NOT EXISTS idx_institutions_location ON institutions(location)",
        "CREATE INDEX IF NOT EXISTS idx_hospitals_type ON hospitals(type)",
        "CREATE INDEX IF NOT EXISTS idx_restaurants_cuisine ON restaurants(cuisine)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
```

### Debugging Tools

#### 1. Logging Configuration

```python
import logging
import sys
from datetime import datetime

def setup_debug_logging():
    """Setup comprehensive debug logging"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    log_filename = f"logs/debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('agent').setLevel(logging.DEBUG)
    logging.getLogger('tools').setLevel(logging.DEBUG)
    logging.getLogger('utils').setLevel(logging.DEBUG)
```

#### 2. Performance Profiling

```python
import cProfile
import pstats
from functools import wraps

def profile_performance(func):
    """Decorator to profile function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
            
            # Save profiling results
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(10)  # Top 10 functions
        
        return result
    return wrapper

# Usage
@profile_performance
def process_query(query: str):
    """Process query with performance profiling"""
    # Implementation here
    pass
```

#### 3. Memory Profiling

```python
import tracemalloc
from contextlib import contextmanager

@contextmanager
def memory_profiler():
    """Context manager for memory profiling"""
    tracemalloc.start()
    
    try:
        yield
    finally:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
        print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")

# Usage
with memory_profiler():
    agent.query("How many universities in Dhaka?")
```

## ⚡ Performance Optimization

### Database Optimization

#### 1. Indexing Strategy

```python
def create_performance_indexes():
    """Create indexes for optimal query performance"""
    indexes = {
        'institutions': [
            'CREATE INDEX IF NOT EXISTS idx_inst_name ON institutions(name)',
            'CREATE INDEX IF NOT EXISTS idx_inst_type ON institutions(type)',
            'CREATE INDEX IF NOT EXISTS idx_inst_location ON institutions(location)',
            'CREATE INDEX IF NOT EXISTS idx_inst_established ON institutions(established)',
            'CREATE INDEX IF NOT EXISTS idx_inst_public_private ON institutions(public_private)'
        ],
        'hospitals': [
            'CREATE INDEX IF NOT EXISTS idx_hosp_name ON hospitals(name)',
            'CREATE INDEX IF NOT EXISTS idx_hosp_type ON hospitals(type)',
            'CREATE INDEX IF NOT EXISTS idx_hosp_location ON hospitals(location)',
            'CREATE INDEX IF NOT EXISTS idx_hosp_bed_capacity ON hospitals(bed_capacity)',
            'CREATE INDEX IF NOT EXISTS idx_hosp_emergency ON hospitals(emergency_services)'
        ],
        'restaurants': [
            'CREATE INDEX IF NOT EXISTS idx_rest_name ON restaurants(name)',
            'CREATE INDEX IF NOT EXISTS idx_rest_cuisine ON restaurants(cuisine)',
            'CREATE INDEX IF NOT EXISTS idx_rest_location ON restaurants(location)',
            'CREATE INDEX IF NOT EXISTS idx_rest_rating ON restaurants(rating)',
            'CREATE INDEX IF NOT EXISTS idx_rest_price_range ON restaurants(price_range)'
        ]
    }
    
    for table, index_list in indexes.items():
        for index_sql in index_list:
            cursor.execute(index_sql)
```

#### 2. Query Optimization

```python
def optimize_sql_query(query: str) -> str:
    """Optimize SQL query for better performance"""
    # Add LIMIT to prevent large result sets
    if 'LIMIT' not in query.upper():
        query += ' LIMIT 1000'
    
    # Use specific columns instead of SELECT *
    if 'SELECT *' in query:
        query = query.replace('SELECT *', 'SELECT id, name, type, location')
    
    return query
```

### Caching Optimization

#### 1. Cache Strategy

```python
class OptimizedCacheManager:
    """Optimized cache manager with intelligent eviction"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with LRU tracking"""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with size management"""
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = {
            'value': value,
            'expires': time.time() + ttl,
            'created': time.time()
        }
        self.access_times[key] = time.time()
    
    def _evict_lru(self):
        """Evict least recently used items"""
        oldest_key = min(self.access_times, key=self.access_times.get)
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
```

### Memory Optimization

#### 1. Connection Pooling

```python
class DatabaseConnectionPool:
    """Database connection pool for better resource management"""
    
    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self.connections = []
        self.available = []
        self.in_use = []
    
    def get_connection(self, db_path: str) -> sqlite3.Connection:
        """Get connection from pool"""
        if self.available:
            conn = self.available.pop()
            self.in_use.append(conn)
            return conn
        
        if len(self.connections) < self.max_connections:
            conn = sqlite3.connect(db_path)
            self.connections.append(conn)
            self.in_use.append(conn)
            return conn
        
        raise Exception("Maximum connections reached")
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return connection to pool"""
        if conn in self.in_use:
            self.in_use.remove(conn)
            self.available.append(conn)
```

## 🔒 Security Best Practices

### SQL Injection Prevention

#### 1. Parameterized Queries

```python
def safe_query_execution(query: str, params: tuple = ()) -> List[Dict]:
    """Execute SQL query safely with parameter binding"""
    try:
        conn = DatabaseManager.create_connection(self.db_path)
        cursor = conn.cursor()
        
        # Validate query type
        if not self._is_safe_query(query):
            raise ValueError("Unsafe query detected")
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def _is_safe_query(self, query: str) -> bool:
    """Validate that query is safe (SELECT only)"""
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
    query_upper = query.upper()
    
    return (query_upper.strip().startswith('SELECT') and 
            not any(keyword in query_upper for keyword in dangerous_keywords))
```

#### 2. Input Validation

```python
import re
from typing import Optional

def validate_query_input(query: str) -> Optional[str]:
    """Validate and sanitize user input"""
    if not query or not isinstance(query, str):
        return None
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>;"\'\\]', '', query)
    
    # Length validation
    if len(sanitized) > 1000:
        return None
    
    # Basic pattern validation
    if not re.match(r'^[a-zA-Z0-9\s\?\.\,\!\-]+$', sanitized):
        return None
    
    return sanitized.strip()
```

### Data Privacy

#### 1. Sensitive Data Handling

```python
import hashlib
import os
from cryptography.fernet import Fernet

class DataProtection:
    """Handle sensitive data protection"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = 'data/.encryption_key'
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for comparison"""
        return hashlib.sha256(data.encode()).hexdigest()
```

## 🚀 Deployment Guide

### Production Deployment

#### 1. Environment Setup

```bash
# Production environment setup
export PYTHONPATH=/path/to/bd-knowledge-agent
export OPENAI_API_KEY=your_production_api_key
export LOG_LEVEL=INFO
export DEBUG=False
export CACHE_ENABLED=True
```

#### 2. Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data cache logs

# Build databases
RUN python scripts/build_databases.py --recreate --sample-data

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  bd-knowledge-agent:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - LOG_LEVEL=INFO
      - DEBUG=False
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache
      - ./logs:/app/logs
    restart: unless-stopped
```

#### 3. Monitoring and Logging

```python
# monitoring.py
import logging
import psutil
from datetime import datetime

class SystemMonitor:
    """Monitor system performance and health"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_system_stats(self):
        """Log system performance statistics"""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        self.logger.info(f"System Stats - CPU: {cpu_percent}%, "
                        f"Memory: {memory.percent}%, "
                        f"Disk: {disk.percent}%")
    
    def check_application_health(self) -> bool:
        """Check application health"""
        try:
            # Test database connectivity
            conn = sqlite3.connect('data/institutions.db')
            conn.close()
            
            # Test cache functionality
            from utils.cache_manager import CacheManager
            cache = CacheManager()
            cache.get_statistics()
            
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
```

## 🤝 Contributing Guidelines

### Code Review Process

#### 1. Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
```

#### 2. Review Guidelines

```python
# Code Review Checklist

## Functionality
- Does the code work as intended?
- Are edge cases handled?
- Is error handling comprehensive?

## Code Quality
- Is the code readable and maintainable?
- Are variable and function names descriptive?
- Is the code properly documented?

## Performance
- Is the code efficient?
- Are there potential performance bottlenecks?
- Is caching used appropriately?

## Security
- Is the code secure?
- Are inputs validated?
- Are sensitive data handled properly?

## Testing
- Are tests comprehensive?
- Do tests cover edge cases?
- Are tests maintainable?
```

### Development Best Practices

#### 1. Code Organization

```python
# ✅ Good: Organized imports
import os
import sys
from typing import Dict, List, Optional

import sqlite3
from langchain.tools import BaseTool

from utils.config import Config
from utils.database import DatabaseManager

# ❌ Bad: Disorganized imports
import sqlite3
import os
from langchain.tools import BaseTool
import sys
from utils.config import Config
from utils.database import DatabaseManager
from typing import Dict, List, Optional
```

#### 2. Error Handling

```python
# ✅ Good: Specific error handling
try:
    result = self._execute_query(sql)
    return result
except sqlite3.OperationalError as e:
    logger.error(f"Database operational error: {e}")
    return []
except sqlite3.IntegrityError as e:
    logger.error(f"Database integrity error: {e}")
    return []
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return []

# ❌ Bad: Generic error handling
try:
    result = self._execute_query(sql)
    return result
except Exception as e:
    print(f"Error: {e}")
    return []
```

---

This development guide provides comprehensive information for developers working with the Bangladesh Knowledge Agent. Follow these guidelines to ensure high-quality, maintainable, and secure code.
