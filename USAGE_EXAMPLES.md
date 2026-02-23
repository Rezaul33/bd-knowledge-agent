# Bangladesh Knowledge Agent - Usage Examples

📚 Comprehensive examples demonstrating the capabilities of the Bangladesh Knowledge Agent.

## 🚀 Quick Start Examples

### Basic Query Processing

```python
from agent.main_agent import BangladeshKnowledgeAgent

# Initialize the agent
agent = BangladeshKnowledgeAgent()

# Simple query
response = agent.query("How many universities are in Dhaka?")
print(response['response'])
# Output: "Found 5 institutions matching your criteria."

# Query with full metadata
response = agent.query("List hospitals with emergency services", include_metadata=True)
print(f"Tool Used: {response['metadata']['tool_used']}")
print(f"Confidence: {response['metadata']['result_confidence']}")
print(f"Execution Time: {response['metadata']['execution_time']}s")
print(f"Cached: {response['metadata']['cached']}")
```

### Interactive Session

```python
# Start interactive mode
agent = BangladeshKnowledgeAgent()

# Multiple queries in a session
queries = [
    "How many universities are in Dhaka?",
    "List hospitals with emergency services",
    "What restaurants serve Italian food?",
    "Find colleges established after 1950"
]

for query in queries:
    print(f"\nQuery: {query}")
    result = agent.query(query)
    print(f"Response: {result['response']}")
    print(f"Confidence: {result['metadata']['result_confidence']}")
```

## 🏛️ Institutions Database Examples

### University Queries

```python
agent = BangladeshKnowledgeAgent()

# Count universities by location
response = agent.query("How many universities are in Dhaka?")
print(response['response'])
# Expected: Found 5 institutions matching your criteria.

# List all universities
response = agent.query("List all universities in Bangladesh")
print(response['response'])
# Expected: Detailed list of all universities with locations

# Filter by establishment year
response = agent.query("Find colleges established after 1950")
print(response['response'])
# Expected: List of institutions established after 1950

# Specific type queries
response = agent.query("What engineering universities are available?")
print(response['response'])
# Expected: Engineering-focused institutions
```

### Advanced Institution Queries

```python
# Complex queries with multiple criteria
response = agent.query("Engineering universities in Dhaka established after 1960")
print(response['response'])

# Location-based queries
response = agent.query("Educational institutions in Chattogram")
print(response['response'])

# Type-specific queries
response = agent.query("Medical colleges in Bangladesh")
print(response['response'])
```

## 🏥 Hospitals Database Examples

### Basic Hospital Queries

```python
agent = BangladeshKnowledgeAgent()

# Service-based queries
response = agent.query("List hospitals with emergency services")
print(response['response'])
# Expected: List of hospitals offering emergency services

# Capacity queries
response = agent.query("Hospitals with more than 1000 beds")
print(response['response'])
# Expected: Large hospitals with bed capacity > 1000

# Type-based queries
response = agent.query("What private hospitals are available?")
print(response['response'])
# Expected: List of private hospitals

# Location-specific queries
response = agent.query("Medical colleges in Dhaka")
print(response['response'])
# Expected: Medical colleges located in Dhaka
```

### Advanced Hospital Queries

```python
# Complex hospital queries
response = agent.query("Teaching hospitals in Dhaka with emergency services")
print(response['response'])

# Facility-specific queries
response = agent.query("Hospitals with ICU facilities")
print(response['response'])

# Location and capacity combination
response = agent.query("Large hospitals in Chattogram")
print(response['response'])
```

## 🍽️ Restaurants Database Examples

### Cuisine and Rating Queries

```python
agent = BangladeshKnowledgeAgent()

# Cuisine-specific queries
response = agent.query("What restaurants serve Italian food?")
print(response['response'])
# Expected: Restaurants serving Italian cuisine

# Rating-based queries
response = agent.query("Bangladeshi restaurants with high ratings")
print(response['response'])
# Expected: Highly-rated Bangladeshi restaurants

# Location and cuisine combination
response = agent.query("What restaurants serve Italian food in Chattogram?")
print(response['response'])
# Expected: Italian restaurants in Chattogram

# Price range queries
response = agent.query("Find restaurants with medium price range")
print(response['response'])
# Expected: Medium-priced restaurants
```

### Advanced Restaurant Queries

```python
# Complex restaurant queries
response = agent.query("High-rated Italian restaurants in Dhaka")
print(response['response'])

# Location-based queries
response = agent.query("Restaurants in Sylhet")
print(response['response'])

# Specific features
response = agent.query("Family-friendly restaurants")
print(response['response'])
```

## 🌐 Web Search Examples

### General Knowledge Queries

```python
agent = BangladeshKnowledgeAgent()

# Policy and governance
response = agent.query("What is healthcare policy of Bangladesh?")
print(response['response'])
# Expected: Information about healthcare policies

# Cultural information
response = agent.query("Cultural festivals in Bangladesh")
print(response['response'])
# Expected: List of major cultural festivals

# Economic information
response = agent.query("Economic policies of Bangladesh")
print(response['response'])
# Expected: Overview of economic policies

# Historical information
response = agent.query("History of Bangladesh liberation war")
print(response['response'])
# Expected: Historical information
```

### Complex Web Search Queries

```python
# Multi-faceted queries
response = agent.query("Impact of digitalization on Bangladesh economy")
print(response['response'])

# Current affairs
response = agent.query("Recent developments in Bangladesh education sector")
print(response['response'])

# Comparative queries
response = agent.query("Bangladesh vs Sri Lanka healthcare system comparison")
print(response['response'])
```

## 🔄 Query Routing and Analysis

### Understanding Query Classification

```python
agent = BangladeshKnowledgeAgent()

# Explain how a query is routed
explanation = agent.explain_routing("How many universities in Dhaka?")
print(explanation)
# Expected: Detailed explanation of routing logic

# Test routing for different query types
queries = [
    "Universities in Dhaka",  # Should route to institutions
    "Hospitals with beds",     # Should route to hospitals
    "Italian restaurants",     # Should route to restaurants
    "Bangladesh economy"       # Should route to web search
]

for query in queries:
    explanation = agent.explain_routing(query)
    print(f"\nQuery: {query}")
    print(f"Routing: {explanation}")
```

### Confidence Score Analysis

```python
agent = BangladeshKnowledgeAgent()

# High confidence queries (simple SQL)
high_confidence_queries = [
    "How many universities are in Dhaka?",
    "List all hospitals",
    "Italian restaurants"
]

# Medium confidence queries (complex SQL)
medium_confidence_queries = [
    "Engineering universities established after 1970",
    "Private hospitals with emergency services",
    "High-rated restaurants in specific areas"
]

# Lower confidence queries (web search)
low_confidence_queries = [
    "Bangladesh economic policy",
    "Cultural significance",
    "Historical context"
]

for query in high_confidence_queries:
    result = agent.query(query)
    print(f"Query: {query}")
    print(f"Confidence: {result['metadata']['result_confidence']}")
    print(f"Expected: High (≥0.80)")
```

## 💾 Caching Examples

### Cache Behavior Demonstration

```python
agent = BangladeshKnowledgeAgent()

# First query - not cached
print("First query (not cached):")
result1 = agent.query("How many universities are in Dhaka?")
print(f"Cached: {result1['metadata']['cached']}")
print(f"Execution Time: {result1['metadata']['execution_time']}s")

# Second identical query - should be cached
print("\nSecond query (should be cached):")
result2 = agent.query("How many universities are in Dhaka?")
print(f"Cached: {result2['metadata']['cached']}")
print(f"Execution Time: {result2['metadata']['execution_time']}s")
print(f"Cache Hits: {result2['metadata']['cache_hits']}")

# Different query - not cached
print("\nDifferent query (not cached):")
result3 = agent.query("How many hospitals are in Dhaka?")
print(f"Cached: {result3['metadata']['cached']}")
print(f"Execution Time: {result3['metadata']['execution_time']}s")
```

### Cache Statistics

```python
# Get cache statistics
cache_stats = agent.cache_manager.get_stats()
print(f"Total Cache Entries: {cache_stats['total_entries']}")
print(f"Valid Entries: {cache_stats['valid_entries']}")
print(f"Average Hit Count: {cache_stats['average_hit_count']}")
print(f"Hit Rate: {cache_stats['hit_rate']}")

# Popular cached queries
print("\nPopular Queries:")
for query in cache_stats['popular_queries']:
    print(f"• {query['query'][:50]}... (Hits: {query['hit_count']})")
```

## 📊 Logging and Analytics Examples

### Query History Analysis

```python
agent = BangladeshKnowledgeAgent()

# Execute some queries
queries = [
    "How many universities in Dhaka?",
    "List hospitals with emergency services",
    "Italian restaurants",
    "Bangladesh economy"
]

for query in queries:
    agent.query(query)

# Get query history
history = agent.get_query_history(limit=10)
print(f"Total Queries in Session: {len(history)}")

for i, entry in enumerate(history, 1):
    print(f"{i}. {entry['query'][:40]}... ({entry['tool_used']})")
    print(f"   Confidence: {entry['result_confidence']:.2f}, Time: {entry['execution_time']:.3f}s")
```

### Session Statistics

```python
# Get session summary
session_summary = agent.query_logger.get_session_summary(agent.session_id)
print(f"Session Summary:")
print(f"• Total Queries: {session_summary['total_queries']}")
print(f"• Average Execution Time: {session_summary['avg_execution_time']}s")
print(f"• Average Confidence: {session_summary['avg_confidence']}")
print(f"• Cache Hit Rate: {session_summary['cache_hit_rate']}%")
print(f"• Error Rate: {session_summary['error_rate']}%")

# Get overall statistics
stats = agent.query_logger.get_statistics(days=7)
print(f"\n7-Day Statistics:")
print(f"• Total Queries: {stats['total_queries']}")
print(f"• Unique Sessions: {stats['unique_sessions']}")
print(f"• Cache Hit Rate: {stats['cache_hit_rate']}%")
print(f"• Error Rate: {stats['error_rate']}%")
```

## 🛠️ Advanced Usage Patterns

### Batch Processing

```python
agent = BangladeshKnowledgeAgent()

# Process multiple queries efficiently
batch_queries = [
    "Universities in Dhaka",
    "Hospitals with emergency services",
    "Italian restaurants",
    "Bangladesh economy",
    "Medical colleges"
]

# Batch processing
results = agent.batch_query(batch_queries)

for i, result in enumerate(results, 1):
    print(f"{i}. Query: {batch_queries[i-1]}")
    print(f"   Success: {result['success']}")
    print(f"   Tool: {result['metadata']['tool_used']}")
    print(f"   Confidence: {result['metadata']['result_confidence']}")
```

### Error Handling

```python
agent = BangladeshKnowledgeAgent()

# Test error handling
error_queries = [
    "",  # Empty query
    "Invalid query with no context",  # Ambiguous query
    "Very complex multi-tool query"  # Complex query
]

for query in error_queries:
    print(f"\nTesting: '{query}'")
    result = agent.query(query)
    
    if result['success']:
        print(f"✅ Success: {result['response'][:100]}...")
    else:
        print(f"❌ Error: {result['response']}")
    
    print(f"Confidence: {result['metadata']['result_confidence']}")
```

### Performance Monitoring

```python
import time

agent = BangladeshKnowledgeAgent()

# Performance test
test_queries = [
    "How many universities in Dhaka?",
    "List hospitals with emergency services",
    "Italian restaurants",
    "Bangladesh economy"
]

execution_times = []
confidences = []

for query in test_queries:
    start_time = time.time()
    result = agent.query(query)
    end_time = time.time()
    
    execution_time = end_time - start_time
    execution_times.append(execution_time)
    confidences.append(result['metadata']['result_confidence'])
    
    print(f"Query: {query}")
    print(f"Time: {execution_time:.3f}s")
    print(f"Confidence: {result['metadata']['result_confidence']:.2f}")

# Performance summary
print(f"\nPerformance Summary:")
print(f"• Average Time: {sum(execution_times)/len(execution_times):.3f}s")
print(f"• Fastest: {min(execution_times):.3f}s")
print(f"• Slowest: {max(execution_times):.3f}s")
print(f"• Average Confidence: {sum(confidences)/len(confidences):.2f}")
```

## 🎯 Best Practices

### Query Optimization

```python
# Good: Specific, clear queries
good_queries = [
    "How many universities are in Dhaka?",
    "List hospitals with emergency services",
    "Italian restaurants with high ratings"
]

# Avoid: Vague or ambiguous queries
avoid_queries = [
    "Tell me about stuff",
    "Information about Bangladesh",
    "Things related to education"
]

# Demonstrate best practices
print("✅ Recommended Query Patterns:")
for query in good_queries:
    result = agent.query(query)
    print(f"• {query} → Confidence: {result['metadata']['result_confidence']:.2f}")

print("\n❌ Query Patterns to Avoid:")
for query in avoid_queries:
    result = agent.query(query)
    print(f"• {query} → Confidence: {result['metadata']['result_confidence']:.2f}")
```

### Session Management

```python
# Create dedicated session for specific tasks
agent = BangladeshKnowledgeAgent()

# Session for educational institution research
education_queries = [
    "Engineering universities in Bangladesh",
    "Medical colleges admission requirements",
    "Private universities in Dhaka"
]

print("Education Research Session:")
for query in education_queries:
    result = agent.query(query)
    print(f"• {query} → {result['metadata']['tool_used']}")

# Get session summary
session_info = agent.get_agent_info()
print(f"\nSession Summary:")
print(f"• Total Queries: {session_info['total_queries']}")
print(f"• Session ID: {session_info['session_id']}")
```

## 🔧 Customization Examples

### Configuration Changes

```python
# Example of custom configuration
from utils.config import Config

# Modify cache settings
Config.CACHE_ENABLED = True
Config.CACHE_TTL = 7200  # 2 hours

# Modify logging settings
Config.LOG_LEVEL = "DEBUG"

# Create agent with custom settings
agent = BangladeshKnowledgeAgent()

# Test with new settings
result = agent.query("How many universities in Dhaka?")
print(f"Result with custom config: {result['metadata']['cached']}")
```

### Tool-Specific Queries

```python
# Test specific tool routing
agent = BangladeshKnowledgeAgent()

# Institutions-specific queries
institution_queries = [
    "universities in dhaka",
    "engineering colleges",
    "medical schools"
]

print("🏛️ Institutions Database Test:")
for query in institution_queries:
    result = agent.query(query)
    print(f"• {query} → {result['metadata']['tool_used']}")

# Hospitals-specific queries
hospital_queries = [
    "emergency services",
    "bed capacity",
    "icu facilities"
]

print("\n🏥 Hospitals Database Test:")
for query in hospital_queries:
    result = agent.query(query)
    print(f"• {query} → {result['metadata']['tool_used']}")
```

---

📚 **More Examples**: Check the test files for additional usage patterns:
- `test_comprehensive.py` - Full test suite
- `test_validation_report.py` - Validation examples
- Individual tool test files for specific functionality

🎯 **Tip**: Start with simple queries and gradually move to more complex ones to understand the agent's capabilities and limitations.
