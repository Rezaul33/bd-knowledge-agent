"""
Validation Report Generator - Detailed analysis of test results
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.main_agent import BangladeshKnowledgeAgent

def generate_validation_report():
    """Generate comprehensive validation report"""
    agent = BangladeshKnowledgeAgent()
    
    print("📋 Bangladesh Knowledge Agent - Validation Report")
    print("=" * 60)
    print(f"Generated: {datetime.now().isoformat()}")
    print(f"Session ID: {agent.session_id[:12]}...")
    print("=" * 60)
    
    # Test Categories
    test_categories = {
        "Institutions Database": [
            ("Count universities in Dhaka", "How many universities are in Dhaka?"),
            ("List all universities", "List all universities in Bangladesh"),
            ("Find colleges after 1950", "Find colleges established after 1950"),
            ("Engineering universities", "What engineering universities are available?")
        ],
        "Hospitals Database": [
            ("Emergency services", "List hospitals with emergency services"),
            ("Large hospitals", "Hospitals with more than 1000 beds"),
            ("Medical colleges", "Medical colleges in Dhaka"),
            ("Private hospitals", "What private hospitals are available?")
        ],
        "Restaurants Database": [
            ("Italian restaurants", "What restaurants serve Italian food?"),
            ("High-rated restaurants", "Bangladeshi restaurants with high ratings"),
            ("Restaurants in Chattogram", "What restaurants serve Italian food in Chattogram?"),
            ("Budget restaurants", "Find restaurants with medium price range")
        ],
        "Web Search": [
            ("Healthcare policy", "What is healthcare policy of Bangladesh?"),
            ("Cultural festivals", "Cultural festivals in Bangladesh"),
            ("Economic policies", "Economic policies of Bangladesh")
        ],
        "Edge Cases": [
            ("Empty query", ""),
            ("Ambiguous query", "Tell me about stuff"),
            ("Complex query", "How many engineering universities in Dhaka have emergency hospitals nearby with Italian restaurants?")
        ]
    }
    
    # Run tests and collect results
    all_results = {}
    category_stats = {}
    
    for category, tests in test_categories.items():
        print(f"\n🧪 Testing {category}...")
        category_results = []
        
        for test_name, query in tests:
            print(f"\n📋 {test_name}")
            print(f"Query: {query}")
            
            try:
                result = agent.query(query, include_metadata=True)
                
                if result['success']:
                    metadata = result['metadata']
                    test_result = {
                        'name': test_name,
                        'query': query,
                        'success': True,
                        'tool_used': metadata.get('tool_used', ''),
                        'confidence': metadata.get('result_confidence', 0.0),
                        'execution_time': metadata.get('execution_time', 0.0),
                        'cached': metadata.get('cached', False),
                        'response_length': len(result['response']),
                        'response_preview': result['response'][:150] + "..." if len(result['response']) > 150 else result['response']
                    }
                    print(f"✅ Success - Tool: {test_result['tool_used']}, Confidence: {test_result['confidence']:.2f}")
                else:
                    test_result = {
                        'name': test_name,
                        'query': query,
                        'success': False,
                        'error': result['response']
                    }
                    print(f"❌ Failed - {test_result['error']}")
                
                category_results.append(test_result)
                
            except Exception as e:
                test_result = {
                    'name': test_name,
                    'query': query,
                    'success': False,
                    'error': str(e)
                }
                category_results.append(test_result)
                print(f"❌ Error - {e}")
        
        all_results[category] = category_results
        
        # Calculate category statistics
        total_tests = len(category_results)
        passed_tests = sum(1 for r in category_results if r['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        category_stats[category] = {
            'total': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests,
            'success_rate': success_rate
        }
        
        print(f"📊 Category Result: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
    
    # Generate overall statistics
    print(f"\n" + "=" * 60)
    print("📊 OVERALL VALIDATION RESULTS")
    print("=" * 60)
    
    total_tests = sum(stats['total'] for stats in category_stats.values())
    total_passed = sum(stats['passed'] for stats in category_stats.values())
    overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    print(f"Overall Success Rate: {overall_success_rate:.1f}%")
    
    # Category breakdown
    print(f"\n📋 Category Breakdown:")
    for category, stats in category_stats.items():
        status = "✅" if stats['success_rate'] >= 80 else "⚠️" if stats['success_rate'] >= 60 else "❌"
        print(f"{status} {category}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1f}%)")
    
    # Performance analysis
    all_successful = [r for category in all_results.values() for r in category if r['success']]
    if all_successful:
        execution_times = [r['execution_time'] for r in all_successful]
        confidences = [r['confidence'] for r in all_successful]
        
        print(f"\n⏱️ Performance Analysis:")
        print(f"• Average Execution Time: {sum(execution_times)/len(execution_times):.3f}s")
        print(f"• Fastest: {min(execution_times):.3f}s")
        print(f"• Slowest: {max(execution_times):.3f}s")
        
        print(f"\n📈 Confidence Analysis:")
        print(f"• Average Confidence: {sum(confidences)/len(confidences):.2f}")
        print(f"• Highest: {max(confidences):.2f}")
        print(f"• Lowest: {min(confidences):.2f}")
        
        # Confidence distribution
        high_confidence = sum(1 for c in confidences if c >= 0.8)
        medium_confidence = sum(1 for c in confidences if 0.6 <= c < 0.8)
        low_confidence = sum(1 for c in confidences if c < 0.6)
        
        print(f"\n📊 Confidence Distribution:")
        print(f"• High (≥0.8): {high_confidence} ({(high_confidence/len(confidences))*100:.1f}%)")
        print(f"• Medium (0.6-0.8): {medium_confidence} ({(medium_confidence/len(confidences))*100:.1f}%)")
        print(f"• Low (<0.6): {low_confidence} ({(low_confidence/len(confidences))*100:.1f}%)")
    
    # Tool usage analysis
    tool_usage = {}
    for r in all_successful:
        tool = r['tool_used']
        tool_usage[tool] = tool_usage.get(tool, 0) + 1
    
    if tool_usage:
        print(f"\n🛠️ Tool Usage:")
        for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(all_successful)) * 100
            print(f"• {tool}: {count} uses ({percentage:.1f}%)")
    
    # Failed tests analysis
    all_failed = [r for category in all_results.values() for r in category if not r['success']]
    if all_failed:
        print(f"\n❌ Failed Tests Analysis:")
        for test in all_failed:
            print(f"• {test['name']}: {test.get('error', 'Unknown error')}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if overall_success_rate >= 90:
        print("✅ EXCELLENT: Agent is production-ready!")
    elif overall_success_rate >= 80:
        print("👍 GOOD: Agent is nearly production-ready with minor improvements needed.")
    elif overall_success_rate >= 70:
        print("⚠️  ACCEPTABLE: Agent needs improvements before production deployment.")
    else:
        print("❌ NEEDS WORK: Agent requires significant improvements.")
    
    # Specific recommendations based on results
    if category_stats.get("Web Search", {}).get('success_rate', 0) < 80:
        print("• Consider improving web search query routing and fallback handling.")
    
    if category_stats.get("Institutions Database", {}).get('success_rate', 0) < 80:
        print("• Review institutions database queries and SQL generation.")
    
    if any(r['confidence'] < 0.6 for r in all_successful):
        print("• Some queries have low confidence scores - review confidence scoring rules.")
    
    if any(r['execution_time'] > 2.0 for r in all_successful):
        print("• Some queries are slow - consider optimization and caching improvements.")
    
    # Save detailed report
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'session_id': agent.session_id,
        'overall_stats': {
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_tests - total_passed,
            'success_rate': overall_success_rate
        },
        'category_stats': category_stats,
        'all_results': all_results,
        'tool_usage': tool_usage
    }
    
    try:
        with open('validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        print(f"\n💾 Detailed report saved to: validation_report.json")
    except Exception as e:
        print(f"\n⚠️  Could not save report: {e}")
    
    print(f"\n✅ Validation Report Completed!")
    return overall_success_rate

if __name__ == "__main__":
    success_rate = generate_validation_report()
    
    # Exit with appropriate code
    if success_rate >= 80:
        print("\n🎉 Agent validation PASSED!")
        sys.exit(0)
    else:
        print("\n⚠️  Agent validation NEEDS IMPROVEMENT!")
        sys.exit(1)
