"""
Test script for HospitalsDBTool
"""

from tools.hospitals_tool import HospitalsDBTool

def test_hospitals_tool():
    """Test HospitalsDBTool with various queries"""
    
    print("🧪 Testing HospitalsDBTool...")
    
    tool = HospitalsDBTool()
    
    test_queries = [
        "How many hospitals are there?",
        "How many hospitals are in Dhaka?",
        "List top 10 hospitals by bed capacity",
        "Which hospitals have emergency services?",
        "Show private hospitals in Dhaka",
        "What hospitals offer cardiology services?",
        "Find teaching hospitals",
        "How many public hospitals are there?",
        "Hospitals with more than 1000 beds",
        "Hospitals established after 2000"
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
    test_hospitals_tool()
