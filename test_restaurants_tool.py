"""
Test script for RestaurantsDBTool
"""

from tools.restaurants_tool import RestaurantsDBTool

def test_restaurants_tool():
    """Test RestaurantsDBTool with various queries"""
    
    print("🧪 Testing RestaurantsDBTool...")
    
    tool = RestaurantsDBTool()
    
    test_queries = [
        "How many restaurants are there?",
        "Restaurants in Chattogram serving biryani",
        "List all Bangladeshi restaurants",
        "What restaurants have ratings above 4.0?",
        "Show Italian restaurants in Dhaka",
        "Find high-priced restaurants",
        "Restaurants established after 2010",
        "American restaurants in Dhaka",
        "Low-priced restaurants",
        "Highest rated restaurants"
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
    test_restaurants_tool()
