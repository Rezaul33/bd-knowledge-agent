"""
RestaurantsDBTool - LangChain tool for querying Bangladesh restaurants database
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sqlite3
import re
import time
from utils.database import DatabaseManager
from utils.config import Config

class RestaurantsInput(BaseModel):
    """Input schema for RestaurantsDBTool"""
    query: str = Field(description="Natural language query about Bangladesh restaurants")

class RestaurantsDBTool(BaseTool):
    """Tool for querying Bangladesh restaurants database"""
    
    name = "RestaurantsDBTool"
    description = """Use this tool for queries about Bangladesh restaurants and food establishments.
    Handles restaurant names, cuisine types, ratings, location-based queries, and price ranges.
    
    Examples:
    - "Restaurants in Chattogram serving biryani"
    - "List all Bangladeshi restaurants"
    - "What restaurants have ratings above 4.0?"
    - "Show Italian restaurants in Dhaka"
    - "Find high-priced restaurants"
    - "Restaurants established after 2010"
    
    Database schema:
    - name: Restaurant name
    - location: City/District
    - cuisine_type: Type of cuisine (Bangladeshi, Italian, American, etc.)
    - rating: Star rating (0-5)
    - price_range: Low, Medium, High
    - specialties: Special dishes or cuisine focus
    - established: Year established
    - seating_capacity: Number of seats
    """
    
    args_schema = RestaurantsInput
    
    def __init__(self):
        super().__init__()
        # Store configuration as instance attributes that don't conflict with Pydantic
        object.__setattr__(self, '_db_path', Config.RESTAURANTS_DB)
        object.__setattr__(self, '_table_name', "restaurants")
        object.__setattr__(self, '_schema_info', self._get_schema_info())
    
    @property
    def db_path(self):
        return self._db_path
    
    @property
    def table_name(self):
        return self._table_name
    
    @property
    def schema_info(self):
        return self._schema_info
    
    def _get_schema_info(self) -> str:
        """Get database schema information for SQL generation"""
        conn = DatabaseManager.create_connection(self.db_path)
        try:
            schema = DatabaseManager.validate_schema(conn, self.table_name)
            return f"Table: {self.table_name}\nColumns: {', '.join(schema)}"
        finally:
            conn.close()
    
    def _validate_sql(self, sql: str) -> bool:
        """Validate SQL to prevent destructive operations"""
        sql_upper = sql.upper().strip()
        
        # Only allow SELECT queries
        if not sql_upper.startswith('SELECT'):
            return False
        
        # Block dangerous keywords
        dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER',
            'TRUNCATE', 'EXEC', 'EXECUTE', 'UNION', 'MERGE'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
        
        return True
    
    def _generate_sql(self, natural_query: str) -> str:
        """Generate SQL from natural language query"""
        
        # Common query patterns and their SQL equivalents
        query_patterns = [
            # Count queries
            (r'how many.*restaurants?', lambda m: "SELECT COUNT(*) as total FROM restaurants"),
            (r'how many.*restaurants?.*in\s+(\w+)', lambda m: f"SELECT COUNT(*) as total FROM restaurants WHERE location LIKE '%{m.group(1)}%'"),
            (r'how many.*bangladeshi.*restaurants?', lambda m: "SELECT COUNT(*) as total FROM restaurants WHERE cuisine_type LIKE '%Bangladeshi%'"),
            (r'how many.*italian.*restaurants?', lambda m: "SELECT COUNT(*) as total FROM restaurants WHERE cuisine_type LIKE '%Italian%'"),
            (r'how many.*american.*restaurants?', lambda m: "SELECT COUNT(*) as total FROM restaurants WHERE cuisine_type LIKE '%American%'"),
            
            # Location-based queries
            (r'restaurants?.*in\s+(\w+)', lambda m: f"SELECT name, cuisine_type, rating, price_range FROM restaurants WHERE location LIKE '%{m.group(1)}%'"),
            (r'bangladeshi.*restaurants?.*in\s+(\w+)', lambda m: f"SELECT name, rating, specialties FROM restaurants WHERE cuisine_type LIKE '%Bangladeshi%' AND location LIKE '%{m.group(1)}%'"),
            (r'italian.*restaurants?.*in\s+(\w+)', lambda m: f"SELECT name, rating, price_range FROM restaurants WHERE cuisine_type LIKE '%Italian%' AND location LIKE '%{m.group(1)}%'"),
            (r'american.*restaurants?.*in\s+(\w+)', lambda m: f"SELECT name, rating, price_range FROM restaurants WHERE cuisine_type LIKE '%American%' AND location LIKE '%{m.group(1)}%'"),
            
            # Rating-based queries
            (r'.*rating.*above\s+(\d+\.?\d*)', lambda m: f"SELECT name, cuisine_type, rating, location FROM restaurants WHERE rating > {m.group(1)} ORDER BY rating DESC"),
            (r'.*rating.*below\s+(\d+\.?\d*)', lambda m: f"SELECT name, cuisine_type, rating, location FROM restaurants WHERE rating < {m.group(1)} ORDER BY rating DESC"),
            (r'.*rating.*at least\s+(\d+\.?\d*)', lambda m: f"SELECT name, cuisine_type, rating, location FROM restaurants WHERE rating >= {m.group(1)} ORDER BY rating DESC"),
            (r'.*highest.*rated.*restaurants?', lambda m: "SELECT name, cuisine_type, rating, location FROM restaurants ORDER BY rating DESC LIMIT 10"),
            (r'.*lowest.*rated.*restaurants?', lambda m: "SELECT name, cuisine_type, rating, location FROM restaurants ORDER BY rating ASC LIMIT 10"),
            
            # Price range queries
            (r'.*low.*price.*restaurants?', lambda m: "SELECT name, cuisine_type, rating, location FROM restaurants WHERE price_range = 'Low' ORDER BY rating DESC"),
            (r'.*medium.*price.*restaurants?', lambda m: "SELECT name, cuisine_type, rating, location FROM restaurants WHERE price_range = 'Medium' ORDER BY rating DESC"),
            (r'.*high.*price.*restaurants?', lambda m: "SELECT name, cuisine_type, rating, location FROM restaurants WHERE price_range = 'High' ORDER BY rating DESC"),
            (r'.*cheap.*restaurants?', lambda m: "SELECT name, cuisine_type, rating, location FROM restaurants WHERE price_range = 'Low' ORDER BY rating DESC"),
            (r'.*expensive.*restaurants?', lambda m: "SELECT name, cuisine_type, rating, location FROM restaurants WHERE price_range = 'High' ORDER BY rating DESC"),
            
            # Cuisine type queries
            (r'bangladeshi.*restaurants?', lambda m: "SELECT name, location, rating, specialties FROM restaurants WHERE cuisine_type LIKE '%Bangladeshi%' ORDER BY rating DESC"),
            (r'italian.*restaurants?', lambda m: "SELECT name, location, rating, price_range FROM restaurants WHERE cuisine_type LIKE '%Italian%' ORDER BY rating DESC"),
            (r'american.*restaurants?', lambda m: "SELECT name, location, rating, price_range FROM restaurants WHERE cuisine_type LIKE '%American%' ORDER BY rating DESC"),
            (r'middle.*eastern.*restaurants?', lambda m: "SELECT name, location, rating, specialties FROM restaurants WHERE cuisine_type LIKE '%Middle Eastern%' ORDER BY rating DESC"),
            
            # Specialty/food queries
            (r'.*serving.*biryani', lambda m: "SELECT name, location, rating, price_range FROM restaurants WHERE specialties LIKE '%Biriyani%' OR specialties LIKE '%Biryani%' ORDER BY rating DESC"),
            (r'.*serving.*kabab', lambda m: "SELECT name, location, rating, price_range FROM restaurants WHERE specialties LIKE '%Kabab%' ORDER BY rating DESC"),
            (r'.*serving.*grilled', lambda m: "SELECT name, location, rating, price_range FROM restaurants WHERE specialties LIKE '%Grilled%' ORDER BY rating DESC"),
            (r'.*traditional.*bangladeshi', lambda m: "SELECT name, location, rating, specialties FROM restaurants WHERE specialties LIKE '%Traditional Bangladeshi%' ORDER BY rating DESC"),
            
            # Establishment year queries
            (r'.*established.*after\s+(\d{4})', lambda m: f"SELECT name, cuisine_type, location, established FROM restaurants WHERE established > {m.group(1)} ORDER BY established"),
            (r'.*established.*before\s+(\d{4})', lambda m: f"SELECT name, cuisine_type, location, established FROM restaurants WHERE established < {m.group(1)} ORDER BY established DESC"),
            (r'.*established.*in\s+(\d{4})', lambda m: f"SELECT name, cuisine_type, location, established FROM restaurants WHERE established = {m.group(1)}"),
            
            # Seating capacity queries
            (r'.*largest.*by.*seating', lambda m: "SELECT name, location, cuisine_type, seating_capacity FROM restaurants ORDER BY seating_capacity DESC LIMIT 10"),
            (r'.*smallest.*by.*seating', lambda m: "SELECT name, location, cuisine_type, seating_capacity FROM restaurants ORDER BY seating_capacity ASC LIMIT 10"),
            (r'.*more than\s+(\d+)\s*seats?', lambda m: f"SELECT name, location, cuisine_type, seating_capacity FROM restaurants WHERE seating_capacity > {m.group(1)} ORDER BY seating_capacity DESC"),
            (r'.*at least\s+(\d+)\s*seats?', lambda m: f"SELECT name, location, cuisine_type, seating_capacity FROM restaurants WHERE seating_capacity >= {m.group(1)} ORDER BY seating_capacity DESC"),
            
            # General listing queries
            (r'list.*all.*restaurants?', lambda m: "SELECT name, cuisine_type, location, rating FROM restaurants ORDER BY name"),
            (r'show.*all.*restaurants?', lambda m: "SELECT name, cuisine_type, location, rating FROM restaurants ORDER BY name"),
            (r'all.*restaurants?', lambda m: "SELECT name, cuisine_type, location, rating FROM restaurants ORDER BY name"),
        ]
        
        # Try to match patterns
        for pattern, sql_generator in query_patterns:
            match = re.search(pattern, natural_query, re.IGNORECASE)
            if match:
                sql = sql_generator(match)
                if self._validate_sql(sql):
                    return sql
        
        # Default fallback for general queries
        if 'restaurant' in natural_query.lower():
            return "SELECT name, cuisine_type, location, rating FROM restaurants LIMIT 10"
        
        return None
    
    def _format_results(self, results: list, query: str) -> str:
        """Format query results into natural language"""
        if not results:
            return "No restaurants found matching your query."
        
        # Count queries
        if 'COUNT' in query.upper():
            count = results[0]['total']
            return f"Found {count} restaurants matching your criteria."
        
        # Single restaurant
        if len(results) == 1:
            restaurant = results[0]
            response = f"Found 1 restaurant:\n"
            response += f"• {restaurant.get('name', 'Unknown')} - {restaurant.get('cuisine_type', 'Unknown')} in {restaurant.get('location', 'Unknown')}"
            if 'rating' in restaurant and restaurant['rating']:
                response += f" ({restaurant['rating']}★)"
            if 'price_range' in restaurant and restaurant['price_range']:
                response += f", {restaurant['price_range']} price"
            return response
        
        # Multiple restaurants
        response = f"Found {len(results)} restaurants:\n"
        for i, restaurant in enumerate(results[:10], 1):  # Limit to 10 results
            response += f"{i}. {restaurant.get('name', 'Unknown')} - {restaurant.get('cuisine_type', 'Unknown')}"
            if 'location' in restaurant and restaurant['location']:
                response += f" in {restaurant['location']}"
            if 'rating' in restaurant and restaurant['rating']:
                response += f" ({restaurant['rating']}★)"
            if 'price_range' in restaurant and restaurant['price_range']:
                response += f", {restaurant['price_range']}"
            response += "\n"
        
        if len(results) > 10:
            response += f"... and {len(results) - 10} more restaurants."
        
        return response
    
    def _run(self, query: str) -> str:
        """Execute the tool"""
        start_time = time.time()
        
        try:
            # Generate SQL
            sql = self._generate_sql(query)
            if not sql:
                return "I couldn't understand your query about restaurants. Please try rephrasing it."
            
            # Validate SQL
            if not self._validate_sql(sql):
                return "Invalid query detected. Only SELECT queries are allowed."
            
            # Execute query
            conn = DatabaseManager.create_connection(getattr(self, '_db_path'))
            try:
                results = DatabaseManager.execute_query(conn, sql)
                response = self._format_results(results, sql)
                
                # Add metadata
                execution_time = time.time() - start_time
                response += f"\n\n[Query executed in {execution_time:.2f} seconds]"
                
                return response
                
            finally:
                conn.close()
                
        except Exception as e:
            return f"Error querying restaurants database: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version (not implemented)"""
        return self._run(query)
