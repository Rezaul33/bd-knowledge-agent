"""
Confidence Scoring System for Query Results
"""

from typing import Dict, Any, Optional
import re

class ConfidenceScorer:
    """Calculates confidence scores based on execution metrics and result quality"""
    
    def __init__(self):
        self.max_score = 0.95
    
    def calculate_confidence(self, user_query: str, tool_used: str, sql_executed: bool, 
                         fallback_used: bool, result_empty: bool, 
                         generated_answer: str) -> float:
        """
        Calculate confidence score based on multiple factors
        
        Args:
            user_query: Original user query
            tool_used: Tool that was used
            sql_executed: Whether SQL was executed successfully
            fallback_used: Whether fallback logic was triggered
            result_empty: Whether the result was empty
            generated_answer: The generated answer
            
        Returns:
            Confidence score (0.00-0.95)
        """
        
        # Start with base score
        base_score = 0.95
        
        # Rule 1: Never output 1.00
        base_score = min(base_score, self.max_score)
        
        # Rule 2: Fallback logic reduces confidence
        if fallback_used:
            base_score = min(base_score, 0.60)
        
        # Rule 3: SQL execution failure reduces confidence
        if not sql_executed:
            base_score = min(base_score, 0.50)
        
        # Rule 4: Empty result reduces confidence
        if result_empty:
            base_score = min(base_score, 0.70)
        
        # Rule 5: Web search results shouldn't exceed 0.80
        if tool_used.lower() == 'web_search':
            base_score = min(base_score, 0.80)
        
        # Rule 6: Check query complexity
        complexity_penalty = self._calculate_complexity_penalty(user_query)
        base_score -= complexity_penalty
        
        # Rule 7: Check data completeness
        completeness_penalty = self._calculate_completeness_penalty(generated_answer)
        base_score -= completeness_penalty
        
        # Ensure score is within bounds
        final_score = max(0.00, min(base_score, self.max_score))
        
        # Round to 2 decimal places
        return round(final_score, 2)
    
    def _calculate_complexity_penalty(self, query: str) -> float:
        """Calculate penalty based on query complexity"""
        penalty = 0.0
        
        query_lower = query.lower()
        
        # Aggregation queries
        if any(word in query_lower for word in ['count', 'sum', 'average', 'total']):
            penalty += 0.05
        
        # Filtering queries
        if any(word in query_lower for word in ['where', 'filter', 'greater than', 'less than', 'after', 'before']):
            penalty += 0.03
        
        # Complex queries requiring interpretation
        if any(word in query_lower for word in ['compare', 'best', 'highest', 'lowest', 'ranking']):
            penalty += 0.07
        
        # Multiple conditions
        if query_lower.count('and') > 1 or query_lower.count('or') > 1:
            penalty += 0.05
        
        return penalty
    
    def _calculate_completeness_penalty(self, answer: str) -> float:
        """Calculate penalty based on data completeness issues"""
        penalty = 0.0
        
        # Check for unknown/missing values
        if 'unknown' in answer.lower() or answer.count('Unknown') > 2:
            penalty += 0.05
        
        # Check for NULL indicators
        if 'null' in answer.lower() or 'none' in answer.lower():
            penalty += 0.03
        
        # Check for error messages
        if any(error in answer.lower() for error in ['error', 'failed', 'exception']):
            penalty += 0.10
        
        # Check for generic fallback messages
        if any(fallback in answer.lower() for fallback in ['mock response', 'could not understand', 'please try']):
            penalty += 0.08
        
        return penalty
    
    def get_confidence_category(self, score: float) -> str:
        """Get confidence category description"""
        if score >= 0.90:
            return "High confidence - Simple deterministic query"
        elif score >= 0.80:
            return "Good confidence - Moderate SQL query"
        elif score >= 0.70:
            return "Medium confidence - Web-based info or minor ambiguity"
        elif score >= 0.50:
            return "Low confidence - Fallback used or partial uncertainty"
        else:
            return "Very low confidence - Execution errors or high ambiguity"
    
    def explain_score(self, user_query: str, tool_used: str, sql_executed: bool,
                   fallback_used: bool, result_empty: bool, generated_answer: str) -> Dict[str, Any]:
        """Explain how the confidence score was calculated"""
        score = self.calculate_confidence(user_query, tool_used, sql_executed, 
                                     fallback_used, result_empty, generated_answer)
        
        explanation = {
            'final_score': score,
            'category': self.get_confidence_category(score),
            'factors': {
                'base_score': 0.95,
                'fallback_penalty': 0.60 if fallback_used else 0.00,
                'sql_failure_penalty': 0.50 if not sql_executed else 0.00,
                'empty_result_penalty': 0.70 if result_empty else 0.00,
                'web_search_cap': 0.80 if tool_used.lower() == 'web_search' else 0.95,
                'complexity_penalty': self._calculate_complexity_penalty(user_query),
                'completeness_penalty': self._calculate_completeness_penalty(generated_answer)
            }
        }
        
        return explanation

# Test the confidence scorer
def test_confidence_scorer():
    """Test confidence scoring with various scenarios"""
    scorer = ConfidenceScorer()
    
    test_cases = [
        {
            'name': 'Simple SQL query - successful',
            'user_query': 'How many universities are there?',
            'tool_used': 'institutions',
            'sql_executed': True,
            'fallback_used': False,
            'result_empty': False,
            'generated_answer': 'Found 8 universities matching your criteria.'
        },
        {
            'name': 'Complex SQL query - successful',
            'user_query': 'Find hospitals with more than 1000 beds in Dhaka',
            'tool_used': 'hospitals',
            'sql_executed': True,
            'fallback_used': False,
            'result_empty': False,
            'generated_answer': 'Found 3 hospitals with more than 1000 beds in Dhaka.'
        },
        {
            'name': 'Web search query - successful',
            'user_query': 'What is healthcare policy of Bangladesh?',
            'tool_used': 'web_search',
            'sql_executed': False,
            'fallback_used': False,
            'result_empty': False,
            'generated_answer': 'Bangladesh Healthcare Policy Overview: ...'
        },
        {
            'name': 'SQL query with fallback',
            'user_query': 'Medical colleges in Dhaka',
            'tool_used': 'hospitals',
            'sql_executed': False,
            'fallback_used': True,
            'result_empty': False,
            'generated_answer': 'Web Search Results for Medical colleges in Dhaka...'
        },
        {
            'name': 'Empty SQL result',
            'user_query': 'Find restaurants serving sushi in Rajshahi',
            'tool_used': 'restaurants',
            'sql_executed': True,
            'fallback_used': False,
            'result_empty': True,
            'generated_answer': 'No restaurants found matching your query.'
        }
    ]
    
    print("🧪 Testing Confidence Scorer...")
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {case['name']}")
        print("-" * 50)
        
        score = scorer.calculate_confidence(
            case['user_query'], case['tool_used'], case['sql_executed'],
            case['fallback_used'], case['result_empty'], case['generated_answer']
        )
        
        explanation = scorer.explain_score(
            case['user_query'], case['tool_used'], case['sql_executed'],
            case['fallback_used'], case['result_empty'], case['generated_answer']
        )
        
        print(f"📊 Confidence Score: {score}")
        print(f"📝 Category: {explanation['category']}")
        print(f"🔍 Factors: {explanation['factors']}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    test_confidence_scorer()
