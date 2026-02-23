"""
Test script for Query Router
"""

from agent.query_router import QueryRouter

def test_query_router():
    """Test the query router with various queries"""
    
    print("🧪 Testing Query Router...")
    
    router = QueryRouter()
    
    test_queries = [
        "How many universities are in Dhaka?",
        "List all hospitals with emergency services", 
        "What restaurants serve Italian food in Chattogram?",
        "What is the healthcare policy of Bangladesh?",
        "Find colleges established after 1950",
        "Hospitals with more than 1000 beds",
        "Bangladeshi restaurants with high ratings",
        "Cultural festivals in Bangladesh",
        "Medical colleges in Dhaka",
        "Economic policies of Bangladesh"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query}")
        print("-" * 50)
        
        # Get classification
        classification = router.classify_query(query)
        print(f"🎯 Tool: {classification['primary_tool']} (Routing Confidence: {classification['confidence']:.2f})")
        
        # Execute query
        result, tool, final_classification = router.route_query(query)
        print(f"📄 Result Preview (first 200 chars):")
        print(result[:200] + "..." if len(result) > 200 else result)
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_query_router()
