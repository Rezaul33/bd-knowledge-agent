"""
Test script for InstitutionsDBTool
"""

from tools.institutions_tool import InstitutionsDBTool

def test_institutions_tool():
    """Test the InstitutionsDBTool with various queries"""
    
    print("🧪 Testing InstitutionsDBTool...")
    
    tool = InstitutionsDBTool()
    
    test_queries = [
        "How many institutions are there?",
        "How many universities are in Dhaka?",
        "Which institutions offer medical degrees?",
        "List all colleges in Dhaka",
        "What are the government institutions?",
        "Show institutions established after 1950",
        "List all universities",
        "Which institutions offer engineering degrees?",
        "How many colleges are there?",
        "What institutions are in Chattogram?"
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
    test_institutions_tool()
