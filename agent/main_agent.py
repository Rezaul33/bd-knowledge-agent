"""
Main AI Agent - Bangladesh Knowledge Agent with LangChain Agent Executor
"""

import sys
import os
import time
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.query_router import QueryRouter
from tools.institutions_tool import InstitutionsDBTool
from tools.hospitals_tool import HospitalsDBTool
from tools.restaurants_tool import RestaurantsDBTool
from tools.web_search_tool import WebSearchTool
from utils.config import Config
from utils.confidence_scorer import ConfidenceScorer
from utils.cache_manager import CacheManager
from utils.query_logger import QueryLogger

class BangladeshKnowledgeAgent:
    """Main AI Agent for Bangladesh Knowledge System"""
    
    def __init__(self):
        self.query_router = QueryRouter()
        self.confidence_scorer = ConfidenceScorer()
        self.cache_manager = CacheManager()
        self.query_logger = QueryLogger()
        
        # Initialize all tools
        self.tools = [
            InstitutionsDBTool(),
            HospitalsDBTool(), 
            RestaurantsDBTool(),
            WebSearchTool()
        ]
        
        # Agent metadata
        self.agent_name = "Bangladesh Knowledge Agent"
        self.version = "1.0.0"
        self.session_id = self._generate_session_id()
        
        # Query history for context
        self.query_history: List[Dict[str, Any]] = []
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{int(time.time())}_{hash(os.urandom(8))}"
    
    def query(self, user_query: str, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Process user query and return comprehensive response
        
        Args:
            user_query: Natural language query from user
            include_metadata: Whether to include execution metadata
            
        Returns:
            Dictionary with response, metadata, and analysis
        """
        start_time = time.time()
        
        try:
            # Check if query contains multiple questions
            multiple_queries = self._detect_multiple_questions(user_query)
            
            if multiple_queries and len(multiple_queries) > 1:
                # Process multiple queries
                responses = []
                total_execution_time = 0
                
                for sub_query in multiple_queries:
                    sub_start_time = time.time()
                    
                    # Get classification for sub query
                    classification = self.query_router.classify_query(sub_query)
                    
                    # Check cache first
                    tool_name = classification.get('primary_tool', '')
                    # Ensure tool_name is a string, not an object
                    if hasattr(tool_name, 'name'):
                        tool_name = tool_name.name
                    elif hasattr(tool_name, '__class__'):
                        tool_name = tool_name.__class__.__name__
                    
                    cached_result = self.cache_manager.get(sub_query, tool_name)
                    
                    if cached_result and Config.CACHE_ENABLED:
                        # Use cached result
                        result = cached_result['result']
                        execution_time = time.time() - sub_start_time
                        confidence = cached_result['confidence']
                        tool_used = cached_result['tool_used']
                        
                        # Add cache indicator
                        result += f"\n\n[From Cache: True]"
                        result += f"\n[Cache Hits: {cached_result['hit_count']}]"
                        result += f"\n[Confidence: {confidence:.2f}]"
                        
                        response_data = {
                            'query': sub_query,
                            'response': result,
                            'tool_used': tool_used,
                            'routing_confidence': classification.get('confidence'),
                            'result_confidence': confidence,
                            'execution_time': round(execution_time, 3),
                            'timestamp': datetime.now().isoformat(),
                            'session_id': self.session_id,
                            'classification': classification,
                            'cached': True,
                            'cache_hits': cached_result['hit_count']
                        }
                    else:
                        # Route query through intelligent router
                        result, tool_used, classification = self.query_router.route_query(sub_query)
                        
                        # Calculate execution metrics
                        execution_time = time.time() - sub_start_time
                        
                        # Extract confidence from result or calculate new one
                        if '[Confidence:' in result:
                            confidence_str = result.split('[Confidence:')[1].strip().replace(']', '')
                            confidence = float(confidence_str)
                        else:
                            # Calculate confidence based on execution
                            sql_executed = classification.get('primary_tool') != 'web_search'
                            fallback_used = classification.get('fallback_used', False)
                            result_empty = "No" in result or "not found" in result.lower()
                            confidence = self.confidence_scorer.calculate_confidence(
                                sub_query, classification.get('primary_tool', ''), 
                                sql_executed, fallback_used, result_empty, result
                            )
                            result += f"\n\n[Confidence: {confidence:.2f}]"
                        
                        # Cache the result if caching is enabled
                        if Config.CACHE_ENABLED:
                            # Ensure tool_used is a string
                            tool_used_str = tool_used
                            if hasattr(tool_used, 'name'):
                                tool_used_str = tool_used.name
                            elif hasattr(tool_used, '__class__'):
                                tool_used_str = tool_used.__class__.__name__
                            
                            self.cache_manager.set(
                                sub_query, tool_used_str, result, confidence, execution_time
                            )
                        
                        # Prepare response metadata
                        response_data = {
                            'query': sub_query,
                            'response': result,
                            'tool_used': tool_used_str if 'tool_used_str' in locals() else str(tool_used),
                            'routing_confidence': classification.get('confidence'),
                            'result_confidence': confidence,
                            'execution_time': round(execution_time, 3),
                            'timestamp': datetime.now().isoformat(),
                            'session_id': self.session_id,
                            'classification': classification,
                            'cached': False,
                            'cache_hits': 0
                        }
                    
                    responses.append(response_data)
                    total_execution_time += execution_time
                
                # Combine all responses
                combined_response = self._format_multiple_query_response(user_query, responses)
                
                # Calculate overall metrics
                avg_confidence = sum(r['result_confidence'] for r in responses) / len(responses)
                
                combined_metadata = {
                    'query': user_query,
                    'response': combined_response,
                    'tool_used': 'multiple',
                    'routing_confidence': 0.0,
                    'result_confidence': avg_confidence,
                    'execution_time': round(total_execution_time, 3),
                    'timestamp': datetime.now().isoformat(),
                    'session_id': self.session_id,
                    'classification': {'multiple_queries': True, 'count': len(multiple_queries)},
                    'cached': any(r['cached'] for r in responses),
                    'cache_hits': sum(r['cache_hits'] for r in responses),
                    'sub_responses': responses
                }
                
                # Add to query history
                self.query_history.append(combined_metadata)
                
                # Log the query
                self.query_logger.log_query(combined_metadata)
                
                # Format final response
                if include_metadata:
                    formatted_response = self._format_response_with_metadata(combined_metadata)
                else:
                    formatted_response = combined_response
                
                return {
                    'success': True,
                    'response': formatted_response,
                    'metadata': combined_metadata
                }
            
            else:
                # Process single query (existing logic)
                return self._process_single_query(user_query, include_metadata, start_time)
            
        except Exception as e:
            error_time = time.time() - start_time
            error_response = {
                'query': user_query,
                'response': f"Error processing query: {str(e)}",
                'tool_used': 'error',
                'routing_confidence': 0.0,
                'result_confidence': 0.0,
                'execution_time': round(error_time, 3),
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'error': str(e)
            }
            
            return {
                'success': False,
                'response': f"Error: {str(e)}",
                'metadata': error_response
            }
    
    def _clean_response_for_web(self, response: str) -> str:
        """Clean response for web interface by removing CLI metadata"""
        # Remove CLI-formatted metadata
        if '[Query executed in' in response:
            response = response.split('[Query executed in')[0].strip()
        if '[Confidence:' in response:
            response = response.split('[Confidence:')[0].strip()
        if '[From Cache:' in response:
            response = response.split('[From Cache:')[0].strip()
        if '[Cache Hits:' in response:
            response = response.split('[Cache Hits:')[0].strip()
        
        # Remove any remaining metadata separators
        response = response.split('---')[0].strip() if '---' in response else response.strip()
        
        return response
    
    def _format_response_with_metadata(self, response_data: Dict[str, Any]) -> str:
        """Format response with metadata"""
        response = response_data['response']
        
        # Add metadata section
        metadata_section = f"""
---
📊 Query Analysis:
• Tool Used: {response_data['tool_used'].title()}
• Routing Confidence: {response_data['routing_confidence']:.2f}
• Result Confidence: {response_data['result_confidence']:.2f}
• Execution Time: {response_data['execution_time']}s
• Session: {response_data['session_id'][:12]}...
        """.strip()
        
        return f"{response}\n{metadata_section}"
    
    def _format_multiple_query_response(self, user_query: str, responses: List[Dict[str, Any]]) -> str:
        """Format response for multiple queries"""
        combined_response = ""
        
        for i, response in enumerate(responses, 1):
            # Clean the response content to remove CLI metadata
            content = response['response']
            if '[Query executed in' in content:
                content = content.split('[Query executed in')[0].strip()
            if '[Confidence:' in content:
                content = content.split('[Confidence:')[0].strip()
            if '---' in content:
                content = content.split('---')[0].strip()
            
            combined_response += f"**Query {i}: {response['query']}**\n\n"
            combined_response += content
            combined_response += "\n\n"
        
        return combined_response.strip()
    
    def _detect_multiple_questions(self, user_query: str) -> List[str]:
        """Detect multiple questions in a single query"""
        # Simple implementation: split by '?' and remove empty strings
        multiple_queries = [q.strip() for q in user_query.split('?') if q.strip()]
        
        return multiple_queries
    
    def _process_single_query(self, user_query: str, include_metadata: bool, start_time: float) -> Dict[str, Any]:
        """Process single query (existing logic)"""
        try:
            # Get classification first
            classification = self.query_router.classify_query(user_query)
            
            # Check cache first
            tool_name = classification.get('primary_tool', '')
            # Ensure tool_name is a string, not an object
            if hasattr(tool_name, 'name'):
                tool_name = tool_name.name
            elif hasattr(tool_name, '__class__'):
                tool_name = tool_name.__class__.__name__
            
            cached_result = self.cache_manager.get(user_query, tool_name)
            
            if cached_result and Config.CACHE_ENABLED:
                # Use cached result
                result = cached_result['result']
                execution_time = time.time() - start_time
                confidence = cached_result['confidence']
                tool_used = cached_result['tool_used']
                
                # Add cache indicator
                result += f"\n\n[From Cache: True]"
                result += f"\n[Cache Hits: {cached_result['hit_count']}]"
                result += f"\n[Confidence: {confidence:.2f}]"
                
                response_data = {
                    'query': user_query,
                    'response': result,
                    'tool_used': tool_used,
                    'routing_confidence': classification.get('confidence'),
                    'result_confidence': confidence,
                    'execution_time': round(execution_time, 3),
                    'timestamp': datetime.now().isoformat(),
                    'session_id': self.session_id,
                    'classification': classification,
                    'cached': True,
                    'cache_hits': cached_result['hit_count']
                }
            else:
                # Route query through intelligent router
                result, tool_used, classification = self.query_router.route_query(user_query)
                
                # Calculate execution metrics
                execution_time = time.time() - start_time
                
                # Extract confidence from result or calculate new one
                if '[Confidence:' in result:
                    confidence_str = result.split('[Confidence:')[1].strip().replace(']', '')
                    confidence = float(confidence_str)
                else:
                    # Calculate confidence based on execution
                    sql_executed = classification.get('primary_tool') != 'web_search'
                    fallback_used = classification.get('fallback_used', False)
                    result_empty = "No" in result or "not found" in result.lower()
                    confidence = self.confidence_scorer.calculate_confidence(
                        user_query, classification.get('primary_tool', ''), 
                        sql_executed, fallback_used, result_empty, result
                    )
                    result += f"\n\n[Confidence: {confidence:.2f}]"
                
                # Cache the result if caching is enabled
                if Config.CACHE_ENABLED:
                    # Ensure tool_used is a string
                    tool_used_str = tool_used
                    if hasattr(tool_used, 'name'):
                        tool_used_str = tool_used.name
                    elif hasattr(tool_used, '__class__'):
                        tool_used_str = tool_used.__class__.__name__
                    
                    self.cache_manager.set(
                        user_query, tool_used_str, result, confidence, execution_time
                    )
                
                # Prepare response metadata
                response_data = {
                    'query': user_query,
                    'response': result,
                    'tool_used': tool_used_str if 'tool_used_str' in locals() else str(tool_used),
                    'routing_confidence': classification.get('confidence'),
                    'result_confidence': confidence,
                    'execution_time': round(execution_time, 3),
                    'timestamp': datetime.now().isoformat(),
                    'session_id': self.session_id,
                    'classification': classification,
                    'cached': False,
                    'cache_hits': 0
                }
            
            # Add to query history
            self.query_history.append(response_data)
            
            # Log the query
            self.query_logger.log_query(response_data)
            
            # Format final response
            if include_metadata:
                formatted_response = self._format_response_with_metadata(response_data)
            else:
                # For web interface, return clean response without CLI metadata
                formatted_response = self._clean_response_for_web(result)
            
            return {
                'success': True,
                'response': formatted_response,
                'metadata': response_data
            }
            
        except Exception as e:
            error_time = time.time() - start_time
            error_response = {
                'query': user_query,
                'response': f"Error processing query: {str(e)}",
                'tool_used': 'error',
                'routing_confidence': 0.0,
                'result_confidence': 0.0,
                'execution_time': round(error_time, 3),
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'error': str(e)
            }
            
            return {
                'success': False,
                'response': f"Error: {str(e)}",
                'metadata': error_response
            }
    
    def _clean_response_for_web(self, response: str) -> str:
        """Clean response for web interface by removing CLI metadata"""
        # Remove CLI-formatted metadata
        if '[Query executed in' in response:
            response = response.split('[Query executed in')[0].strip()
        if '[Confidence:' in response:
            response = response.split('[Confidence:')[0].strip()
        if '[From Cache:' in response:
            response = response.split('[From Cache:')[0].strip()
        if '[Cache Hits:' in response:
            response = response.split('[Cache Hits:')[0].strip()
        
        # Remove any remaining metadata separators
        response = response.split('---')[0].strip() if '---' in response else response.strip()
        
        return response
    
    def _format_response_with_metadata(self, response_data: Dict[str, Any]) -> str:
        """Format response with metadata"""
        response = response_data['response']
        
        # Add metadata section
        metadata_section = f"""
---
📊 Query Analysis:
• Tool Used: {response_data['tool_used'].title()}
• Routing Confidence: {response_data['routing_confidence']:.2f}
• Result Confidence: {response_data['result_confidence']:.2f}
• Execution Time: {response_data['execution_time']}s
• Session: {response_data['session_id'][:12]}...
        """.strip()
        
        return f"{response}\n{metadata_section}"
    
    def get_query_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent query history"""
        return self.query_history[-limit:]
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information and capabilities"""
        return {
            'name': self.agent_name,
            'version': self.version,
            'capabilities': [
                'Institution queries (universities, colleges, schools)',
                'Hospital queries (medical facilities, bed capacity, services)',
                'Restaurant queries (cuisine types, ratings, locations)',
                'General knowledge queries (policies, history, culture)',
                'Intelligent query routing and classification',
                'Confidence scoring',
                'Response time tracking'
            ],
            'tools_available': [
                'InstitutionsDBTool',
                'HospitalsDBTool', 
                'RestaurantsDBTool',
                'WebSearchTool'
            ],
            'databases': {
                'institutions': Config.INSTITUTIONS_DB,
                'hospitals': Config.HOSPITALS_DB,
                'restaurants': Config.RESTAURANTS_DB
            },
            'session_id': self.session_id,
            'total_queries': len(self.query_history)
        }
    
    def batch_query(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Process multiple queries in batch"""
        results = []
        for query in queries:
            result = self.query(query, include_metadata=False)
            results.append(result)
        return results
    
    def explain_routing(self, query: str) -> str:
        """Explain how a query would be routed"""
        return self.query_router.explain_routing(query)

# Interactive agent interface
def interactive_agent():
    """Interactive command-line interface for the agent"""
    agent = BangladeshKnowledgeAgent()
    
    print(f"🤖 {agent.agent_name} v{agent.version}")
    print(f"📋 Session: {agent.session_id[:12]}...")
    print("💬 Type 'quit' to exit, 'help' for commands, 'info' for agent info")
    print("="*60)
    
    while True:
        try:
            user_input = input("\n🔍 Your query: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("""
📚 Available Commands:
• help - Show this help message
• info - Show agent information
• history - Show query history
• explain <query> - Explain query routing
• stats - Show session statistics
• quit - Exit the agent

💡 Example Queries:
• How many universities are in Dhaka?
• List hospitals with emergency services
• What restaurants serve Italian food?
• What is healthcare policy of Bangladesh?
                """)
                continue
            elif user_input.lower() == 'info':
                info = agent.get_agent_info()
                print(f"\n🤖 Agent Information:")
                print(f"Name: {info['name']}")
                print(f"Version: {info['version']}")
                print(f"Session: {info['session_id'][:12]}...")
                print(f"Total Queries: {info['total_queries']}")
                print("\n🛠️ Capabilities:")
                for cap in info['capabilities']:
                    print(f"• {cap}")
                continue
            elif user_input.lower() == 'history':
                history = agent.get_query_history()
                print(f"\n📜 Recent Queries ({len(history)}):")
                for i, item in enumerate(history, 1):
                    print(f"{i}. {item['query']} ({item['tool_used']})")
                continue
            elif user_input.lower().startswith('explain '):
                query = user_input[7:].strip()
                explanation = agent.explain_routing(query)
                print(f"\n🔍 Routing Explanation:\n{explanation}")
                continue
            elif user_input.lower() == 'stats':
                history = agent.get_query_history()
                if history:
                    avg_time = sum(item['metadata']['execution_time'] for item in history) / len(history)
                    avg_confidence = sum(item['metadata']['result_confidence'] for item in history) / len(history)
                    print(f"\n📊 Session Statistics:")
                    print(f"Total Queries: {len(history)}")
                    print(f"Average Execution Time: {avg_time:.3f}s")
                    print(f"Average Confidence: {avg_confidence:.2f}")
                else:
                    print("\n📊 No queries in this session yet.")
                continue
            
            # Process regular query
            if user_input:
                print("\n🔄 Processing...")
                result = agent.query(user_input)
                print(f"\n📄 Response:\n{result['response']}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

# Test agent functionality
def test_agent():
    """Test the agent with sample queries"""
    agent = BangladeshKnowledgeAgent()
    
    test_queries = [
        "How many universities are in Dhaka?",
        "List hospitals with emergency services", 
        "What restaurants serve Italian food?",
        "What is healthcare policy of Bangladesh?",
        "Find colleges established after 1950"
    ]
    
    print("🧪 Testing Bangladesh Knowledge Agent...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query}")
        print("-" * 50)
        
        result = agent.query(query, include_metadata=True)
        
        if result['success']:
            print(f"✅ Success")
            print(f"📄 Response Preview (first 200 chars):")
            print(result['response'][:200] + "..." if len(result['response']) > 200 else result['response'])
        else:
            print(f"❌ Failed: {result['response']}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    # Check if running interactively or testing
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_agent()
    else:
        interactive_agent()
