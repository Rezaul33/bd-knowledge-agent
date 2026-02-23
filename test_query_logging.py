"""
Test Query Logging System
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.main_agent import BangladeshKnowledgeAgent

def test_query_logging():
    """Test the query logging functionality"""
    agent = BangladeshKnowledgeAgent()
    
    print("🧪 Testing Query Logging System...")
    
    test_queries = [
        "How many universities are in Dhaka?",
        "List hospitals with emergency services", 
        "What restaurants serve Italian food?",
        "What is healthcare policy of Bangladesh?",
        "Find colleges established after 1950"
    ]
    
    # Execute queries to generate logs
    print(f"\n📝 Executing {len(test_queries)} queries to generate logs...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Query {i}: {query}")
        result = agent.query(query, include_metadata=False)
        print(f"✅ Logged successfully")
    
    # Test logging statistics
    print(f"\n📊 Testing Logging Statistics...")
    stats = agent.query_logger.get_statistics(days=1)
    
    print(f"📈 Statistics for today:")
    print(f"• Total Queries: {stats['total_queries']}")
    print(f"• Unique Sessions: {stats['unique_sessions']}")
    print(f"• Avg Execution Time: {stats['avg_execution_time']}s")
    print(f"• Avg Confidence: {stats['avg_confidence']}")
    print(f"• Cache Hit Rate: {stats['cache_hit_rate']}%")
    print(f"• Error Rate: {stats['error_rate']}%")
    
    print(f"\n🛠️ Tool Distribution:")
    for tool in stats['tool_distribution']:
        print(f"• {tool['tool']}: {tool['count']} queries ({tool['percentage']}%)")
    
    print(f"\n📝 Query Type Distribution:")
    for qtype in stats['query_type_distribution']:
        print(f"• {qtype['type']}: {qtype['count']} queries ({qtype['percentage']}%)")
    
    # Test session summary
    print(f"\n🔍 Testing Session Summary...")
    session_summary = agent.query_logger.get_session_summary(agent.session_id)
    
    print(f"📋 Session Summary:")
    print(f"• Session ID: {session_summary['session_id'][:12]}...")
    print(f"• Total Queries: {session_summary['total_queries']}")
    print(f"• Start Time: {session_summary['start_time']}")
    print(f"• End Time: {session_summary['end_time']}")
    print(f"• Avg Execution Time: {session_summary['avg_execution_time']}s")
    print(f"• Avg Confidence: {session_summary['avg_confidence']}")
    print(f"• Cache Hit Rate: {session_summary['cache_hit_rate']}%")
    
    # Test query history
    print(f"\n📜 Testing Query History...")
    history = agent.query_logger.get_query_history(limit=5)
    
    print(f"📝 Recent Queries ({len(history)}):")
    for i, entry in enumerate(history, 1):
        print(f"{i}. {entry['query_text'][:50]}... ({entry['tool_used']})")
        print(f"   Confidence: {entry['result_confidence']}, Cached: {entry['cached']}")
    
    print(f"\n✅ Query logging system test completed successfully!")

if __name__ == "__main__":
    test_query_logging()
