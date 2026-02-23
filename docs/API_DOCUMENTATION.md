# 📚 API Documentation

## 🤖 BangladeshKnowledgeAgent Class

### Overview

The `BangladeshKnowledgeAgent` is the main class that orchestrates query processing, tool routing, caching, and logging for the Bangladesh Knowledge Agent system.

### Constructor

```python
BangladeshKnowledgeAgent(
    cache_enabled: bool = True,
    cache_ttl: int = 3600,
    log_level: str = "INFO",
    debug: bool = False
)
```

**Parameters:**
- `cache_enabled` (bool): Enable/disable caching system (default: True)
- `cache_ttl` (int): Cache time-to-live in seconds (default: 3600)
- `log_level` (str): Logging level (DEBUG, INFO, WARNING, ERROR) (default: "INFO")
- `debug` (bool): Enable debug mode for verbose output (default: False)

**Example:**
```python
from agent.main_agent import BangladeshKnowledgeAgent

# Initialize with default settings
agent = BangladeshKnowledgeAgent()

# Initialize with custom settings
agent = BangladeshKnowledgeAgent(
    cache_enabled=True,
    cache_ttl=7200,  # 2 hours
    log_level="DEBUG",
    debug=True
)
```

### Core Methods

#### query()

Process a single query and return response with optional metadata.

```python
response = agent.query(
    user_query: str,
    include_metadata: bool = False,
    debug: bool = False
) -> Dict[str, Any]
```

**Parameters:**
- `user_query` (str): The query string to process
- `include_metadata` (bool): Include detailed metadata in response (default: False)
- `debug` (bool): Enable debug information for this query (default: False)

**Returns:**
```python
{
    "success": bool,
    "response": str,
    "metadata": {
        "query": str,
        "tool_used": str,
        "routing_confidence": float,
        "result_confidence": float,
        "execution_time": float,
        "timestamp": str,
        "session_id": str,
        "cached": bool,
        "cache_hits": int,
        "classification": dict,
        "sql_executed": str
    }
}
```

**Example:**
```python
response = agent.query("How many universities are in Dhaka?", include_metadata=True)
print(response['response'])
print(f"Tool: {response['metadata']['tool_used']}")
print(f"Confidence: {response['metadata']['result_confidence']}")
```

#### batch_query()

Process multiple queries in batch and return results.

```python
results = agent.batch_query(
    queries: List[str],
    include_metadata: bool = False
) -> List[Dict[str, Any]]
```

**Parameters:**
- `queries` (List[str]): List of query strings to process
- `include_metadata` (bool): Include detailed metadata for each query (default: False)

**Returns:** List of response dictionaries (same format as query() method)

**Example:**
```python
queries = [
    "How many universities in Dhaka?",
    "List hospitals with emergency services",
    "What restaurants serve Italian food?"
]
results = agent.batch_query(queries, include_metadata=True)
for i, result in enumerate(results, 1):
    print(f"Query {i}: {result['response']}")
```

#### explain_routing()

Get detailed explanation of how a query would be routed.

```python
explanation = agent.explain_routing(query: str) -> Dict[str, Any]
```

**Parameters:**
- `query` (str): Query string to analyze

**Returns:**
```python
{
    "query": str,
    "tool_scores": {
        "institutions": float,
        "hospitals": float,
        "restaurants": float,
        "web_search": float
    },
    "primary_tool": str,
    "confidence": float,
    "question_type": str,
    "has_location": bool,
    "location_detected": str,
    "classification": dict
}
```

**Example:**
```python
explanation = agent.explain_routing("Compare hospital inflation impact")
print(f"Primary tool: {explanation['primary_tool']}")
print(f"Confidence: {explanation['confidence']}")
print(f"Tool scores: {explanation['tool_scores']}")
```

#### get_agent_info()

Get information about the agent configuration and capabilities.

```python
info = agent.get_agent_info() -> Dict[str, Any]
```

**Returns:**
```python
{
    "version": str,
    "tools": List[str],
    "cache_enabled": bool,
    "cache_ttl": int,
    "log_level": str,
    "debug_mode": bool,
    "session_id": str,
    "databases": {
        "institutions": str,
        "hospitals": str,
        "restaurants": str
    }
}
```

**Example:**
```python
info = agent.get_agent_info()
print(f"Agent Version: {info['version']}")
print(f"Available Tools: {', '.join(info['tools'])}")
print(f"Cache Enabled: {info['cache_enabled']}")
```

#### get_query_history()

Get query history with optional filtering.

```python
history = agent.get_query_history(
    limit: int = 10,
    include_metadata: bool = True,
    session_id: str = None
) -> List[Dict[str, Any]]
```

**Parameters:**
- `limit` (int): Maximum number of queries to return (default: 10)
- `include_metadata` (bool): Include detailed metadata (default: True)
- `session_id` (str): Filter by specific session ID (default: None)

**Returns:** List of query history entries

**Example:**
```python
history = agent.get_query_history(limit=5, include_metadata=True)
for query in history:
    print(f"Query: {query['query']}")
    print(f"Tool: {query['tool_used']}")
    print(f"Timestamp: {query['timestamp']}")
```

#### get_session_stats()

Get statistics for a specific session or overall.

```python
stats = agent.get_session_stats(session_id: str = None) -> Dict[str, Any]
```

**Parameters:**
- `session_id` (str): Session ID to get stats for (default: current session)

**Returns:**
```python
{
    "session_id": str,
    "total_queries": int,
    "avg_confidence": float,
    "avg_execution_time": float,
    "most_used_tool": str,
    "cache_hit_rate": float,
    "queries_by_tool": dict,
    "confidence_distribution": dict,
    "start_time": str,
    "last_query_time": str
}
```

**Example:**
```python
stats = agent.get_session_stats()
print(f"Total queries: {stats['total_queries']}")
print(f"Average confidence: {stats['avg_confidence']}")
print(f"Most used tool: {stats['most_used_tool']}")
```

## 🛠️ Tool Classes

### InstitutionsDBTool

Tool for querying educational institutions database.

```python
from tools.institutions_tool import InstitutionsDBTool

tool = InstitutionsDBTool()
result = tool._run("How many universities in Dhaka?")
```

**Supported Query Types:**
- Count queries: "How many universities are in Dhaka?"
- List queries: "List all universities in Bangladesh"
- Filter queries: "Find colleges established after 1950"
- Location queries: "Universities in Dhaka"
- Degree queries: "Which institutions offer medical degrees?"

**Database Schema:**
```python
{
    "name": "TEXT",           # Institution name
    "type": "TEXT",           # University, College, Government Institution
    "location": "TEXT",       # City/District
    "established": "INTEGER", # Year established
    "degrees_offered": "TEXT", # Types of degrees available
    "students_count": "INTEGER", # Number of students
    "public_private": "TEXT", # Public or Private
    "specialization": "TEXT"  # Field of specialization
}
```

### HospitalsDBTool

Tool for querying hospitals database.

```python
from tools.hospitals_tool import HospitalsDBTool

tool = HospitalsDBTool()
result = tool._run("List hospitals with emergency services")
```

**Supported Query Types:**
- Service queries: "Hospitals with emergency services"
- Capacity queries: "Hospitals with more than 1000 beds"
- Type queries: "Private hospitals in Dhaka"
- Specialty queries: "Hospitals offering cardiology"
- Location queries: "Medical colleges in Dhaka"

**Database Schema:**
```python
{
    "name": "TEXT",              # Hospital name
    "type": "TEXT",              # Hospital type
    "location": "TEXT",          # City/District
    "bed_capacity": "INTEGER",   # Number of beds
    "emergency_services": "TEXT", # Emergency service availability
    "specialties": "TEXT",       # Medical specialties
    "public_private": "TEXT",    # Public or Private
    "established": "INTEGER"      # Year established
}
```

### RestaurantsDBTool

Tool for querying restaurants database.

```python
from tools.restaurants_tool import RestaurantsDBTool

tool = RestaurantsDBTool()
result = tool._run("What restaurants serve Italian food?")
```

**Supported Query Types:**
- Cuisine queries: "Restaurants serving Italian food"
- Rating queries: "High-rated restaurants in Dhaka"
- Location queries: "Restaurants in Chattogram"
- Price queries: "Restaurants with medium price range"
- Specialty queries: "Fine dining establishments"

**Database Schema:**
```python
{
    "name": "TEXT",           # Restaurant name
    "cuisine": "TEXT",        # Cuisine type
    "location": "TEXT",       # City/Area
    "rating": "REAL",         # Rating (1-5)
    "price_range": "TEXT",    # Budget, Medium, Expensive
    "specialties": "TEXT",    # Special dishes
    "established": "INTEGER"  # Year established
}
```

### WebSearchTool

Tool for general web search queries.

```python
from tools.web_search_tool import WebSearchTool

tool = WebSearchTool()
result = tool._run("What is healthcare policy of Bangladesh?")
```

**Supported Query Types:**
- Policy queries: "Healthcare policy of Bangladesh"
- General knowledge: "Cultural festivals in Bangladesh"
- Economic queries: "Economic growth trends"
- Current events: "Latest news about Bangladesh"
- Historical queries: "History of Bangladesh independence"

**API Providers:**
- Tavily (primary)
- SerpAPI (fallback)
- Bing Search (secondary fallback)
- Mock responses (testing)

## 🔧 Utility Classes

### CacheManager

Manages SQLite-based caching system.

```python
from utils.cache_manager import CacheManager

cache = CacheManager()

# Store in cache
cache.set(query, tool_name, result, confidence, execution_time)

# Retrieve from cache
cached_result = cache.get(query, tool_name)

# Get statistics
stats = cache.get_statistics()

# Clear cache
cache.clear_all()
cache.clear_expired()
```

**Methods:**
- `get(query: str, tool_name: str) -> Optional[Dict]`: Retrieve cached result
- `set(query: str, tool_name: str, result: str, confidence: float, execution_time: float)`: Store result
- `clear_all()`: Clear all cache entries
- `clear_expired()`: Clear expired entries
- `get_statistics() -> Dict`: Get cache statistics

### QueryLogger

Handles comprehensive query logging.

```python
from utils.query_logger import QueryLogger

logger = QueryLogger()

# Log query
logger.log_query(response_data)

# Get session statistics
stats = logger.get_session_stats(session_id)

# Export data
logger.export_to_csv("analytics.csv")
logger.export_to_json("analytics.json")
```

**Methods:**
- `log_query(response_data: Dict)`: Log query with metadata
- `get_session_stats(session_id: str) -> Dict`: Get session statistics
- `get_query_history(limit: int = 10) -> List`: Get query history
- `export_to_csv(filename: str)`: Export to CSV format
- `export_to_json(filename: str)`: Export to JSON format

### ConfidenceScorer

Calculates confidence scores for query results.

```python
from utils.confidence_scorer import ConfidenceScorer

scorer = ConfidenceScorer()

# Calculate confidence
confidence = scorer.calculate_confidence(
    query, tool_used, sql_executed, fallback_used, result_empty, result
)
```

**Scoring Factors:**
- SQL execution success
- Tool routing confidence
- Result completeness
- Query clarity
- Historical performance

## 📊 Response Formats

### Success Response

```python
{
    "success": True,
    "response": "Natural language response to the query",
    "metadata": {
        "query": "Original query text",
        "tool_used": "Name of tool that processed the query",
        "routing_confidence": 0.95,
        "result_confidence": 0.90,
        "execution_time": 0.05,
        "timestamp": "2026-02-23T18:00:00",
        "session_id": "session_12345",
        "cached": False,
        "cache_hits": 0,
        "classification": {
            "primary_tool": "institutions",
            "confidence": 0.95,
            "question_type": "count",
            "has_location": True,
            "location_detected": "Dhaka"
        },
        "sql_executed": "SELECT COUNT(*) as total FROM institutions WHERE type LIKE '%University%' AND location LIKE '%Dhaka%'"
    }
}
```

### Error Response

```python
{
    "success": False,
    "response": "Error message describing what went wrong",
    "metadata": {
        "query": "Original query text",
        "tool_used": "Error",
        "routing_confidence": 0.00,
        "result_confidence": 0.00,
        "execution_time": 0.01,
        "timestamp": "2026-02-23T18:00:00",
        "session_id": "session_12345",
        "cached": False,
        "cache_hits": 0,
        "error": "Detailed error information"
    }
}
```

## 🔍 Error Handling

### Common Error Types

1. **Database Connection Errors**
   - SQLite file not found
   - Permission denied
   - Database corruption

2. **API Key Errors**
   - Missing OpenAI API key
   - Invalid API key format
   - API rate limits

3. **Query Processing Errors**
   - Invalid SQL syntax
   - Tool execution failure
   - Network connectivity issues

4. **Cache Errors**
   - Cache database corruption
   - Disk space issues
   - Permission problems

### Error Response Structure

```python
{
    "success": False,
    "response": "Human-readable error message",
    "metadata": {
        "error": {
            "type": "DatabaseConnectionError",
            "message": "Detailed technical error",
            "traceback": "Stack trace (if debug mode)",
            "timestamp": "2026-02-23T18:00:00"
        }
    }
}
```

## 🚀 Performance Considerations

### Caching Strategy

- **TTL-based expiration**: Default 1 hour
- **LRU eviction**: When cache size limit reached
- **Automatic cleanup**: Periodic removal of expired entries
- **Hit tracking**: Performance monitoring

### Query Optimization

- **SQL indexing**: Optimized database queries
- **Connection pooling**: Efficient database connections
- **Batch processing**: Multiple queries optimization
- **Async support**: Non-blocking operations

### Memory Management

- **Lazy loading**: Tools loaded on demand
- **Resource cleanup**: Automatic memory management
- **Connection limits**: Database connection pooling
- **Cache limits**: Size-based eviction

## 🔒 Security Features

### SQL Injection Prevention

- **Parameter binding**: Safe SQL execution
- **Query validation**: Input sanitization
- **Keyword blocking**: Dangerous SQL commands blocked
- **SELECT-only**: No destructive operations allowed

### Data Privacy

- **Local storage**: All data stored locally
- **No data retention**: Optional query history clearing
- **Session isolation**: User session separation
- **API key protection**: Secure credential management

## 📈 Monitoring and Analytics

### Performance Metrics

- **Query execution time**: Average and percentiles
- **Cache hit rates**: Efficiency monitoring
- **Tool usage statistics**: Usage patterns
- **Error rates**: Reliability tracking

### Session Analytics

- **Query patterns**: User behavior analysis
- **Tool preferences**: Popular features
- **Geographic distribution**: Location-based queries
- **Time-based patterns**: Usage trends

### Export Capabilities

- **CSV export**: Spreadsheet-compatible data
- **JSON export**: Structured data format
- **Real-time monitoring**: Live dashboard data
- **Historical analysis**: Long-term trends

---

This API documentation provides comprehensive information for developers working with the Bangladesh Knowledge Agent. For more examples and usage patterns, see the USAGE_EXAMPLES.md file.
