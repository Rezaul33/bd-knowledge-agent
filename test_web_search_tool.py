"""
Test script for WebSearchTool
"""

from tools.web_search_tool import WebSearchTool

def test_web_search_tool():
    """Test WebSearchTool with various queries"""
    
    print("🧪 Testing WebSearchTool...")
    
    tool = WebSearchTool()
    
    test_queries = [
        "What is the healthcare policy of Bangladesh?",
        "What is the role of DGHS?",
        "Bangladesh education system overview",
        "Cultural festivals in Bangladesh",
        "History of Dhaka University",
        "Bangladesh economic policies",
        "Current weather in Dhaka",  # General knowledge
        "Bangladesh population statistics"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query}")
        print("-" * 50)
        
        try:
            result = tool._run(query)
            print(result)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_web_search_tool()
