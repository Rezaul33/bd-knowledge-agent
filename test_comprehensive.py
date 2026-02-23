"""
Comprehensive Test Suite - Complete validation of Bangladesh Knowledge Agent
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.main_agent import BangladeshKnowledgeAgent

class ComprehensiveTestSuite:
    """Comprehensive test suite for the Bangladesh Knowledge Agent"""
    
    def __init__(self):
        self.agent = BangladeshKnowledgeAgent()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    def run_test(self, test_name: str, query: str, expected_tool: str = None, 
                 min_confidence: float = 0.5, max_execution_time: float = 5.0):
        """Run a single test and record results"""
        self.total_tests += 1
        
        print(f"\n📋 Test {self.total_tests}: {test_name}")
        print(f"Query: {query}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            result = self.agent.query(query, include_metadata=True)
            execution_time = time.time() - start_time
            
            if result['success']:
                # Extract metadata
                metadata = result['metadata']
                tool_used = metadata.get('tool_used', '').lower()
                confidence = metadata.get('result_confidence', 0.0)
                cached = metadata.get('cached', False)
                
                # Validation checks
                checks = {
                    'success': True,
                    'tool_match': expected_tool is None or expected_tool.lower() in tool_used,
                    'confidence_valid': confidence >= min_confidence and confidence <= 0.95,
                    'execution_time_valid': execution_time <= max_execution_time,
                    'response_not_empty': len(result['response'].strip()) > 0,
                    'metadata_complete': all(key in metadata for key in [
                        'query', 'tool_used', 'routing_confidence', 
                        'result_confidence', 'execution_time', 'timestamp'
                    ])
                }
                
                # Determine if test passed
                test_passed = all(checks.values())
                
                if test_passed:
                    self.passed_tests += 1
                    status = "✅ PASSED"
                else:
                    status = "❌ FAILED"
                
                # Record result
                test_result = {
                    'test_name': test_name,
                    'query': query,
                    'status': status,
                    'execution_time': round(execution_time, 3),
                    'tool_used': tool_used,
                    'confidence': confidence,
                    'cached': cached,
                    'checks': checks,
                    'response_preview': result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
                }
                
                # Print results
                print(f"Status: {status}")
                print(f"Tool Used: {tool_used}")
                print(f"Confidence: {confidence:.2f}")
                print(f"Execution Time: {execution_time:.3f}s")
                print(f"Cached: {cached}")
                print(f"Response Preview: {test_result['response_preview']}")
                
                if not test_passed:
                    print(f"\n❌ Failed Checks:")
                    for check_name, passed in checks.items():
                        if not passed:
                            print(f"  • {check_name}: FAILED")
                
            else:
                # Query failed
                test_result = {
                    'test_name': test_name,
                    'query': query,
                    'status': "❌ FAILED",
                    'error': result['response'],
                    'checks': {'success': False}
                }
                
                print(f"Status: ❌ FAILED")
                print(f"Error: {result['response']}")
            
            self.test_results.append(test_result)
            
        except Exception as e:
            # Exception occurred
            test_result = {
                'test_name': test_name,
                'query': query,
                'status': "❌ ERROR",
                'error': str(e),
                'checks': {'success': False}
            }
            
            print(f"Status: ❌ ERROR")
            print(f"Exception: {e}")
            
            self.test_results.append(test_result)
        
        print("=" * 60)
    
    def run_comprehensive_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Bangladesh Knowledge Agent - Comprehensive Test Suite")
        print("=" * 60)
        print(f"Session ID: {self.agent.session_id[:12]}...")
        print(f"Test Started: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Institutions Tests
        print("\n🏛️  INSTITUTIONS DATABASE TESTS")
        self.run_test("Count Universities in Dhaka", 
                     "How many universities are in Dhaka?", 
                     "institutions", 0.8, 2.0)
        
        self.run_test("List All Universities", 
                     "List all universities in Bangladesh", 
                     "institutions", 0.8, 2.0)
        
        self.run_test("Find Colleges After 1950", 
                     "Find colleges established after 1950", 
                     "institutions", 0.8, 2.0)
        
        self.run_test("Engineering Universities", 
                     "What engineering universities are available?", 
                     "institutions", 0.7, 2.0)
        
        # Hospitals Tests
        print("\n🏥 HOSPITALS DATABASE TESTS")
        self.run_test("Hospitals with Emergency Services", 
                     "List hospitals with emergency services", 
                     "hospitals", 0.8, 2.0)
        
        self.run_test("Large Hospitals", 
                     "Hospitals with more than 1000 beds", 
                     "hospitals", 0.8, 2.0)
        
        self.run_test("Medical Colleges", 
                     "Medical colleges in Dhaka", 
                     "hospitals", 0.7, 2.0)
        
        self.run_test("Private Hospitals", 
                     "What private hospitals are available?", 
                     "hospitals", 0.7, 2.0)
        
        # Restaurants Tests
        print("\n🍽️  RESTAURANTS DATABASE TESTS")
        self.run_test("Italian Restaurants", 
                     "What restaurants serve Italian food?", 
                     "restaurants", 0.8, 2.0)
        
        self.run_test("High-Rated Restaurants", 
                     "Bangladeshi restaurants with high ratings", 
                     "restaurants", 0.7, 2.0)
        
        self.run_test("Restaurants in Chattogram", 
                     "What restaurants serve Italian food in Chattogram?", 
                     "restaurants", 0.7, 2.0)
        
        self.run_test("Budget Restaurants", 
                     "Find restaurants with medium price range", 
                     "restaurants", 0.7, 2.0)
        
        # Web Search Tests
        print("\n🌐 WEB SEARCH TESTS")
        self.run_test("Healthcare Policy", 
                     "What is healthcare policy of Bangladesh?", 
                     "web_search", 0.5, 3.0)
        
        self.run_test("Cultural Festivals", 
                     "Cultural festivals in Bangladesh", 
                     "web_search", 0.5, 3.0)
        
        self.run_test("Economic Policies", 
                     "Economic policies of Bangladesh", 
                     "web_search", 0.5, 3.0)
        
        # Edge Cases
        print("\n🔍 EDGE CASE TESTS")
        self.run_test("Empty Query", 
                     "", 
                     None, 0.0, 1.0)
        
        self.run_test("Ambiguous Query", 
                     "Tell me about stuff", 
                     None, 0.3, 2.0)
        
        self.run_test("Complex Query", 
                     "How many engineering universities in Dhaka have emergency hospitals nearby with Italian restaurants?", 
                     None, 0.5, 3.0)
        
        # Caching Test
        print("\n💾 CACHING TESTS")
        self.run_test("Cache Test 1", 
                     "How many universities are in Dhaka?", 
                     "institutions", 0.8, 1.0)  # Should be cached
        
        self.run_test("Cache Test 2", 
                     "How many universities are in Dhaka?", 
                     "institutions", 0.8, 0.5)  # Should be cached and fast
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Tool usage statistics
        tool_stats = {}
        for result in self.test_results:
            if 'tool_used' in result:
                tool = result['tool_used']
                tool_stats[tool] = tool_stats.get(tool, 0) + 1
        
        print(f"\n🛠️ Tool Usage:")
        for tool, count in sorted(tool_stats.items()):
            print(f"• {tool}: {count} tests")
        
        # Performance statistics
        execution_times = [r['execution_time'] for r in self.test_results if 'execution_time' in r]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)
            
            print(f"\n⏱️ Performance:")
            print(f"• Average Execution Time: {avg_time:.3f}s")
            print(f"• Fastest: {min_time:.3f}s")
            print(f"• Slowest: {max_time:.3f}s")
        
        # Confidence statistics
        confidences = [r['confidence'] for r in self.test_results if 'confidence' in r]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            max_confidence = max(confidences)
            min_confidence = min(confidences)
            
            print(f"\n📈 Confidence Scores:")
            print(f"• Average: {avg_confidence:.2f}")
            print(f"• Highest: {max_confidence:.2f}")
            print(f"• Lowest: {min_confidence:.2f}")
        
        # Failed tests
        failed_tests = [r for r in self.test_results if 'FAILED' in r['status'] or 'ERROR' in r['status']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"• {test['test_name']}: {test.get('error', 'Validation failed')}")
        
        # Caching statistics
        cached_tests = [r for r in self.test_results if r.get('cached', False)]
        if cached_tests:
            print(f"\n💾 Caching:")
            print(f"• Cached queries: {len(cached_tests)}")
            print(f"• Cache hit rate: {(len(cached_tests) / self.total_tests) * 100:.1f}%")
        
        print(f"\n✅ Test Suite Completed: {datetime.now().isoformat()}")
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Agent is performing exceptionally well!")
        elif success_rate >= 80:
            print("👍 GOOD: Agent is performing well with minor issues.")
        elif success_rate >= 70:
            print("⚠️  ACCEPTABLE: Agent works but needs improvements.")
        else:
            print("❌ NEEDS WORK: Agent requires significant improvements.")

if __name__ == "__main__":
    test_suite = ComprehensiveTestSuite()
    test_suite.run_comprehensive_tests()
