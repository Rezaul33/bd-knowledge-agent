"""
WebSearchTool - LangChain tool for web search queries using Tavily API
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import time
import os
from utils.config import Config

# Try to import Tavily, fallback to mock if not available
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("Warning: Tavily not installed. WebSearchTool will use mock responses.")

class WebSearchInput(BaseModel):
    """Input schema for WebSearchTool"""
    query: str = Field(description="Natural language query for web search")

class WebSearchTool(BaseTool):
    """Tool for web search queries using Tavily API"""
    
    name = "WebSearchTool"
    description = """Use this tool for general knowledge queries that cannot be answered from the databases.
    Handles policies, definitions, government roles, cultural context, and non-dataset questions.
    
    Examples:
    - "What is the healthcare policy of Bangladesh?"
    - "What is the role of DGHS?"
    - "Bangladesh education system overview"
    - "Cultural festivals in Bangladesh"
    - "Bangladesh economic policies"
    - "History of Dhaka University"
    
    Use this when the query is about:
    - Government policies and regulations
    - Historical information
    - Cultural context
    - General knowledge about Bangladesh
    - Definitions and explanations
    - Current events (if API supports)
    
    Do NOT use for:
    - Specific institution/hospital/restaurant data
    - Counts or statistics from our databases
    - Location-based queries for our datasets
    """
    
    args_schema = WebSearchInput
    
    def __init__(self):
        super().__init__()
        # Store configuration as instance attributes that don't conflict with Pydantic
        object.__setattr__(self, '_client', self._initialize_client())
        object.__setattr__(self, '_mock_responses', self._get_mock_responses())
    
    def _initialize_client(self):
        """Initialize Tavily client"""
        if TAVILY_AVAILABLE and Config.TAVILY_API_KEY:
            try:
                return TavilyClient(api_key=Config.TAVILY_API_KEY)
            except Exception as e:
                print(f"Warning: Failed to initialize Tavily client: {e}")
                return None
        return None
    
    def _get_mock_responses(self) -> Dict[str, str]:
        """Mock responses for testing without API key"""
        return {
            "healthcare policy": """
Bangladesh Healthcare Policy Overview:
- National Health Policy aims to provide universal health coverage
- Directorate General of Health Services (DGHS) is the main implementing body
- Focus on primary healthcare and rural health services
- Public-private partnership model for healthcare delivery
- Health sector programs: Maternal health, Child health, Disease control
- Budget allocation typically around 1% of GDP for healthcare
            """.strip(),
            
            "role of dghs": """
Directorate General of Health Services (DGHS) Role:
- Main government body for healthcare administration in Bangladesh
- Responsible for implementing national health policies
- Manages public hospitals and healthcare facilities
- Coordinates disease control programs
- Oversees medical education and training
- Reports to Ministry of Health and Family Welfare
- Key functions: Healthcare planning, Service delivery, Health regulation
            """.strip(),
            
            "education system": """
Bangladesh Education System Structure:
- Primary Education: Classes 1-5 (6-10 years)
- Junior Secondary: Classes 6-8 (11-13 years)  
- Secondary: Classes 9-10 (14-15 years)
- Higher Secondary: Classes 11-12 (16-17 years)
- Tertiary Education: Universities and Colleges
- Education Boards: Intermediate and Secondary Education Boards
- Ministry of Education oversees the system
- Literacy rate: Approximately 75% (recent estimates)
            """.strip(),
            
            "cultural festivals": """
Major Cultural Festivals in Bangladesh:
- Pohela Boishakh (Bengali New Year) - April 14
- Ekushey February (Language Martyrs Day) - February 21
- Victory Day - December 16
- Independence Day - March 26
- Eid-ul-Fitr and Eid-ul-Azha (Islamic festivals)
- Durga Puja (Hindu festival)
- Buddha Purnima (Buddhist festival)
- Pahela Falgun (Spring festival)
            """.strip(),
            
            "economic policies": """
Bangladesh Economic Policies Overview:
- Export-oriented industrial policy
- Vision 2041: Becoming a developed country
- Digital Bangladesh initiative
- Sustainable Development Goals (SDGs) implementation
- Foreign Direct Investment (FDI) promotion
- Special Economic Zones (SEZs)
- Microfinance and inclusive banking
- Climate change adaptation strategies
            """.strip(),
            
            "dhaka university": """
University of Dhaka - Historical Overview:
- Established: 1921
- Known as the "Oxford of the East"
- First university in Bangladesh (then East Bengal)
- Started with 3 faculties, 12 departments, 3 teachers, 87 students
- Played crucial role in Bengali Language Movement
- Contributed significantly to Independence Movement
- Currently: 13 faculties, 83 departments, 13 institutes
- Student population: Approximately 37,000
- Notable alumni: Sheikh Mujibur Rahman, Tajuddin Ahmed, many others
            """.strip(),
        }
    
    def _search_with_tavily(self, query: str) -> str:
        """Perform actual web search using Tavily"""
        try:
            response = self.client.search(query, search_depth="basic")
            
            if response and 'results' in response and response['results']:
                # Format the search results
                results_text = f"Web Search Results for '{query}':\n\n"
                
                for i, result in enumerate(response['results'][:3], 1):  # Top 3 results
                    title = result.get('title', 'No title')
                    content = result.get('content', 'No content available')
                    url = result.get('url', '')
                    
                    results_text += f"{i}. {title}\n"
                    results_text += f"   {content[:300]}...\n"  # First 300 chars
                    if url:
                        results_text += f"   Source: {url}\n"
                    results_text += "\n"
                
                return results_text
            else:
                return f"No search results found for '{query}'."
                
        except Exception as e:
            return f"Web search failed: {str(e)}"
    
    def _get_mock_response(self, query: str) -> str:
        """Get mock response based on query keywords"""
        query_lower = query.lower()
        mock_responses = getattr(self, '_mock_responses', {})
        
        # Check for keyword matches
        for keywords, response in mock_responses.items():
            if all(keyword in query_lower for keyword in keywords.split()):
                return f"Web Search Results for '{query}':\n\n{response}"
        
        # Default mock response
        return f"""
Web Search Results for '{query}':

This is a mock response since Tavily API is not configured.

To enable real web search:
1. Get a Tavily API key from https://tavily.com
2. Add it to your .env file as TAVILY_API_KEY=your_key_here
3. Install tavily-python: pip install tavily-python

Mock search would typically return:
- Relevant web pages and articles
- Current information about the topic
- Multiple sources with URLs
- Brief descriptions of each result

For Bangladesh-related queries, you'd get information about:
- Government policies and programs
- Cultural and historical context
- Current developments and statistics
- Official government sources
        """.strip()
    
    def _run(self, query: str) -> str:
        """Execute the web search tool"""
        start_time = time.time()
        
        try:
            # Check if we have a real client
            client = getattr(self, '_client', None)
            mock_responses = getattr(self, '_mock_responses', {})
            
            if client:
                response = self._search_with_tavily(query)
            else:
                response = self._get_mock_response(query)
            
            # Add metadata
            execution_time = time.time() - start_time
            response += f"\n\n[Web search completed in {execution_time:.2f} seconds]"
            
            return response
            
        except Exception as e:
            return f"Error performing web search: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version (not implemented)"""
        return self._run(query)
