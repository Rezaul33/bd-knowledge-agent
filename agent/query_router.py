"""
Query Router - Classifies and routes queries to appropriate tools
"""

import re
import sys
import os
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.institutions_tool import InstitutionsDBTool
from tools.hospitals_tool import HospitalsDBTool
from tools.restaurants_tool import RestaurantsDBTool
from tools.web_search_tool import WebSearchTool
from utils.confidence_scorer import ConfidenceScorer

class QueryRouter:
    """Routes queries to appropriate tools based on content analysis"""
    
    def __init__(self):
        self.institutions_tool = InstitutionsDBTool()
        self.hospitals_tool = HospitalsDBTool()
        self.restaurants_tool = RestaurantsDBTool()
        self.web_search_tool = WebSearchTool()
        self.confidence_scorer = ConfidenceScorer()
        
        # Define keyword patterns for each tool
        self.tool_patterns = {
            'institutions': [
                'university', 'college', 'institution', 'education', 'school',
                'academic', 'student', 'faculty', 'degree', 'campus',
                'educational', 'university of', 'college of', 'institute of'
            ],
            'hospitals': [
                'hospital', 'medical', 'healthcare', 'clinic', 'doctor',
                'nurse', 'patient', 'bed', 'emergency', 'surgery',
                'medical college', 'health center', 'hospital in', 'medical facility'
            ],
            'restaurants': [
                'restaurant', 'food', 'dining', 'eat', 'meal', 'cuisine',
                'menu', 'dish', 'cooking', 'chef', 'restaurant in',
                'food in', 'eat in', 'dining in', 'cuisine in'
            ],
            'web_search': [
                'policy', 'policies', 'government', 'history', 'cultural',
                'festival', 'economy', 'economic', 'development', 'statistics',
                'population', 'weather', 'news', 'current', 'what is', 'who is',
                'when was', 'how to', 'definition', 'overview', 'background',
                'inflation', 'impact', 'compare', 'analysis', 'trend', 'growth',
                'market', 'finance', 'investment', 'cost', 'price', 'budget'
            ]
        }
        
        # Location keywords (Bangladesh specific)
        self.location_keywords = [
            'dhaka', 'chattogram', 'chittagong', 'rajshahi', 'khulna',
            'sylhet', 'barisal', 'rangpur', 'mymensingh', 'bangladesh',
            'in dhaka', 'in chattogram', 'in chittagong', 'in rajshahi',
            'in khulna', 'in sylhet', 'in barisal', 'in rangpur',
            'in mymensingh', 'in bangladesh'
        ]
        
        # Question patterns
        self.question_patterns = {
            'count': [
                r'how many', r'number of', r'count of', r'total number',
                r'how much', r'quantity of'
            ],
            'list': [
                r'list all', r'show all', r'all', r'find all',
                r'get all', r'display all'
            ],
            'specific': [
                r'which', r'what', r'where', r'find', r'search',
                r'locate', r'identify', r'show me'
            ],
            'comparison': [
                r'compare', r'best', r'top', r'highest', r'lowest',
                r'most', r'least', r'ranking', r'better'
            ]
        }
    
    def classify_query(self, query: str) -> Dict[str, any]:
        """Classify query type and determine best tool"""
        query_lower = query.lower()
        
        # Initialize scores
        tool_scores = {
            'institutions': 0,
            'hospitals': 0,
            'restaurants': 0,
            'web_search': 0
        }
        
        # Score each tool based on keyword matches
        for tool, keywords in self.tool_patterns.items():
            for keyword in keywords:
                if keyword in query_lower:
                    # Give higher weight to economic/analysis keywords for web search
                    if tool == 'web_search' and keyword in ['inflation', 'impact', 'compare', 'analysis', 'trend', 'growth', 'market', 'finance', 'investment', 'cost', 'price', 'budget']:
                        tool_scores[tool] += 3  # Higher weight for economic terms
                    else:
                        tool_scores[tool] += 1
        
        # Bonus for location-specific queries (more likely database queries)
        location_bonus = 0
        for location in self.location_keywords:
            if location in query_lower:
                location_bonus += 1
        
        # Check for analysis/economic patterns - prioritize web search
        analysis_keywords = ['inflation', 'impact', 'compare', 'analysis', 'trend', 'growth', 'market', 'finance', 'investment', 'cost', 'price', 'budget']
        has_analysis_keywords = any(keyword in query_lower for keyword in analysis_keywords)
        
        if has_analysis_keywords:
            tool_scores['web_search'] += 5  # Strong bonus for analysis queries
            tool_scores['institutions'] -= 1
            tool_scores['hospitals'] -= 1
            tool_scores['restaurants'] -= 1
        elif location_bonus > 0:
            tool_scores['institutions'] += 2
            tool_scores['hospitals'] += 2
            tool_scores['restaurants'] += 2
            tool_scores['web_search'] -= 1
        
        # Identify question type
        question_type = self._identify_question_type(query)
        
        # Determine primary tool
        primary_tool = max(tool_scores, key=tool_scores.get)
        confidence = tool_scores[primary_tool] / sum(tool_scores.values()) if sum(tool_scores.values()) > 0 else 0
        
        # Fallback logic
        if confidence < 0.3 or tool_scores[primary_tool] == 0:
            primary_tool = 'web_search'
            confidence = 0.5
        
        return {
            'primary_tool': primary_tool,
            'confidence': confidence,
            'tool_scores': tool_scores,
            'question_type': question_type,
            'has_location': location_bonus > 0,
            'location_detected': self._extract_location(query)
        }
    
    def _identify_question_type(self, query: str) -> str:
        """Identify the type of question being asked"""
        query_lower = query.lower()
        
        for q_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return q_type
        
        return 'general'
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query"""
        query_lower = query.lower()
        
        for location in self.location_keywords:
            if location in query_lower:
                return location
        
        return None
    
    def route_query(self, query: str) -> Tuple[str, any, Dict]:
        """Route query to appropriate tool and execute"""
        classification = self.classify_query(query)
        tool_name = classification['primary_tool']
        
        # Get appropriate tool
        tool_map = {
            'institutions': self.institutions_tool,
            'hospitals': self.hospitals_tool,
            'restaurants': self.restaurants_tool,
            'web_search': self.web_search_tool
        }
        
        tool = tool_map.get(tool_name)
        if not tool:
            return "Error: Tool not found", None, classification
        
        try:
            # Execute tool
            result = tool._run(query)
            
            # Calculate confidence score
            sql_executed = tool_name != 'web_search'
            fallback_used = False
            result_empty = "No" in result or "not found" in result.lower()
            
            confidence = self.confidence_scorer.calculate_confidence(
                query, tool_name, sql_executed, fallback_used, result_empty, result
            )
            
            # Add confidence to result
            result_with_confidence = f"{result}\n\n[Confidence: {confidence:.2f}]"
            
            return result_with_confidence, tool, {**classification, 'confidence': confidence}
            
        except Exception as e:
            # Fallback to web search on error
            try:
                result = self.web_search_tool._run(query)
                confidence = self.confidence_scorer.calculate_confidence(
                    query, 'web_search', False, True, False, result
                )
                result_with_confidence = f"{result}\n\n[Confidence: {confidence:.2f}]"
                return result_with_confidence, self.web_search_tool, {**classification, 'fallback_used': True, 'confidence': confidence}
            except Exception as fallback_error:
                confidence = 0.00
                return f"Error: {str(e)} (Fallback also failed: {str(fallback_error)})\n\n[Confidence: {confidence:.2f}]", None, {**classification, 'confidence': confidence}
    
    def get_tool_recommendations(self, query: str) -> List[Dict]:
        """Get recommendations for multiple tools with confidence scores"""
        classification = self.classify_query(query)
        
        recommendations = []
        for tool, score in classification['tool_scores'].items():
            if score > 0:
                confidence = score / sum(classification['tool_scores'].values()) if sum(classification['tool_scores'].values()) > 0 else 0
                recommendations.append({
                    'tool': tool,
                    'confidence': confidence,
                    'score': score
                })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        return recommendations
    
    def explain_routing(self, query: str) -> str:
        """Explain why a query was routed to a specific tool"""
        classification = self.classify_query(query)
        
        explanation = f"Query Analysis for: '{query}'\n\n"
        explanation += f"Primary Tool: {classification['primary_tool'].title()}\n"
        explanation += f"Confidence: {classification['confidence']:.2f}\n"
        explanation += f"Question Type: {classification['question_type']}\n"
        explanation += f"Has Location: {classification['has_location']}\n"
        
        if classification['location_detected']:
            explanation += f"Location: {classification['location_detected'].title()}\n"
        
        explanation += "\nTool Scores:\n"
        for tool, score in classification['tool_scores'].items():
            explanation += f"  {tool.title()}: {score}\n"
        
        return explanation

# Test the router
def test_query_router():
    """Test the query router with various queries"""
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
    
    print("🧪 Testing Query Router...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query}")
        print("-" * 50)
        
        # Get classification
        classification = router.classify_query(query)
        print(f"🎯 Tool: {classification['primary_tool']} (Routing Confidence: {classification['confidence']:.2f})")
        
        # Get routing explanation
        explanation = router.explain_routing(query)
        print(explanation)
        
        # Execute query
        result, tool, final_classification = router.route_query(query)
        print(f"\n📄 Result Preview (first 200 chars):")
        print(result[:200] + "..." if len(result) > 200 else result)
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_query_router()
