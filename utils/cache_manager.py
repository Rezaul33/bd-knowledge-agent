"""
Cache Manager - SQLite-based caching system for query results
"""

import sqlite3
import hashlib
import json
import time
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.database import DatabaseManager

class CacheManager:
    """SQLite-based cache manager for query results"""
    
    def __init__(self, cache_db_path: str = None):
        self.cache_db_path = cache_db_path or Config.CACHE_DB
        self.ttl_seconds = Config.CACHE_TTL
        self._initialize_cache_db()
    
    def _initialize_cache_db(self):
        """Initialize cache database with proper schema"""
        conn = DatabaseManager.create_connection(self.cache_db_path)
        try:
            cursor = conn.cursor()
            
            # Create cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT UNIQUE NOT NULL,
                    query_text TEXT NOT NULL,
                    tool_used TEXT NOT NULL,
                    result TEXT NOT NULL,
                    confidence REAL,
                    execution_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_hash ON query_cache(query_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON query_cache(expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tool_used ON query_cache(tool_used)')
            
            conn.commit()
        finally:
            conn.close()
    
    def _generate_query_hash(self, query: str, tool_used: str) -> str:
        """Generate unique hash for query-tool combination"""
        # Ensure tool_used is a string
        tool_name = tool_used.name if hasattr(tool_used, 'name') else str(tool_used)
        hash_input = f"{query.lower().strip()}:{tool_name.lower()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def get(self, query: str, tool_used: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result for query
        
        Args:
            query: The query text
            tool_used: The tool that would be used
            
        Returns:
            Cached result data or None if not found/expired
        """
        query_hash = self._generate_query_hash(query, tool_used)
        
        conn = DatabaseManager.create_connection(self.cache_db_path)
        try:
            cursor = conn.cursor()
            
            # Check if cached result exists and is not expired
            cursor.execute('''
                SELECT query_text, tool_used, result, confidence, execution_time,
                       hit_count, created_at, expires_at
                FROM query_cache 
                WHERE query_hash = ? AND expires_at > datetime('now')
            ''', (query_hash,))
            
            row = cursor.fetchone()
            
            if row:
                # Update hit count and last accessed time
                cursor.execute('''
                    UPDATE query_cache 
                    SET hit_count = hit_count + 1, last_accessed = datetime('now')
                    WHERE query_hash = ?
                ''', (query_hash,))
                conn.commit()
                
                return {
                    'query': row[0],
                    'tool_used': row[1],
                    'result': row[2],
                    'confidence': row[3],
                    'execution_time': row[4],
                    'hit_count': row[5] + 1,
                    'created_at': row[6],
                    'expires_at': row[7],
                    'cached': True
                }
            
            return None
            
        finally:
            conn.close()
    
    def set(self, query: str, tool_used: str, result: str, 
             confidence: float, execution_time: float) -> bool:
        """
        Store query result in cache
        
        Args:
            query: The query text
            tool_used: Tool that generated the result
            result: The result text
            confidence: Confidence score
            execution_time: Execution time in seconds
            
        Returns:
            True if cached successfully, False otherwise
        """
        query_hash = self._generate_query_hash(query, tool_used)
        expires_at = datetime.now() + timedelta(seconds=self.ttl_seconds)
        
        conn = DatabaseManager.create_connection(self.cache_db_path)
        try:
            cursor = conn.cursor()
            
            # Insert or replace cache entry
            cursor.execute('''
                INSERT OR REPLACE INTO query_cache 
                (query_hash, query_text, tool_used, result, confidence, 
                 execution_time, expires_at, hit_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, datetime('now'))
            ''', (query_hash, query, tool_used, result, confidence, 
                  execution_time, expires_at.isoformat()))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Cache error: {e}")
            return False
        finally:
            conn.close()
    
    def invalidate(self, query: str, tool_used: str) -> bool:
        """Remove specific query from cache"""
        query_hash = self._generate_query_hash(query, tool_used)
        
        conn = DatabaseManager.create_connection(self.cache_db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM query_cache WHERE query_hash = ?', (query_hash,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def clear_expired(self) -> int:
        """Remove all expired entries from cache"""
        conn = DatabaseManager.create_connection(self.cache_db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM query_cache WHERE expires_at <= datetime("now")')
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def clear_all(self) -> int:
        """Clear all cache entries"""
        conn = DatabaseManager.create_connection(self.cache_db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM query_cache')
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        conn = DatabaseManager.create_connection(self.cache_db_path)
        try:
            cursor = conn.cursor()
            
            # Total entries
            cursor.execute('SELECT COUNT(*) FROM query_cache')
            total_entries = cursor.fetchone()[0]
            
            # Valid entries (not expired)
            cursor.execute('SELECT COUNT(*) FROM query_cache WHERE expires_at > datetime("now")')
            valid_entries = cursor.fetchone()[0]
            
            # Expired entries
            expired_entries = total_entries - valid_entries
            
            # Average hit count
            cursor.execute('SELECT AVG(hit_count) FROM query_cache')
            avg_hit_count = cursor.fetchone()[0] or 0
            
            # Most popular queries
            cursor.execute('''
                SELECT query_text, tool_used, hit_count 
                FROM query_cache 
                ORDER BY hit_count DESC 
                LIMIT 5
            ''')
            popular_queries = cursor.fetchall()
            
            # Cache hit rate (approximate)
            cursor.execute('SELECT SUM(hit_count) FROM query_cache')
            total_hits = cursor.fetchone()[0] or 0
            hit_rate = (total_hits / max(total_entries, 1)) if total_entries > 0 else 0
            
            return {
                'total_entries': total_entries,
                'valid_entries': valid_entries,
                'expired_entries': expired_entries,
                'average_hit_count': round(avg_hit_count, 2),
                'total_hits': total_hits,
                'hit_rate': round(hit_rate, 2),
                'popular_queries': [
                    {
                        'query': row[0][:50] + '...' if len(row[0]) > 50 else row[0],
                        'tool_used': row[1],
                        'hit_count': row[2]
                    }
                    for row in popular_queries
                ],
                'cache_db_path': self.cache_db_path,
                'ttl_seconds': self.ttl_seconds
            }
            
        finally:
            conn.close()
    
    def get_cache_info(self, query: str, tool_used: str) -> Optional[Dict[str, Any]]:
        """Get cache information for specific query"""
        query_hash = self._generate_query_hash(query, tool_used)
        
        conn = DatabaseManager.create_connection(self.cache_db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT created_at, expires_at, hit_count, last_accessed
                FROM query_cache WHERE query_hash = ?
            ''', (query_hash,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'cached': True,
                    'created_at': row[0],
                    'expires_at': row[1],
                    'hit_count': row[2],
                    'last_accessed': row[3],
                    'time_to_expiry': self._calculate_time_to_expiry(row[1])
                }
            else:
                return {'cached': False}
                
        finally:
            conn.close()
    
    def _calculate_time_to_expiry(self, expires_at: str) -> str:
        """Calculate human-readable time to expiry"""
        try:
            expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            now = datetime.now()
            
            if expiry_time <= now:
                return "Expired"
            
            delta = expiry_time - now
            
            if delta.days > 0:
                return f"{delta.days} days {delta.seconds // 3600} hours"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600} hours {(delta.seconds % 3600) // 60} minutes"
            else:
                return f"{delta.seconds // 60} minutes"
                
        except:
            return "Unknown"

# Test the cache manager
def test_cache_manager():
    """Test cache manager functionality"""
    cache = CacheManager("cache/test_cache.db")
    
    print("🧪 Testing Cache Manager...")
    
    # Test 1: Cache miss
    print("\n📋 Test 1: Cache miss")
    result = cache.get("How many universities in Dhaka?", "institutions")
    print(f"Result: {result}")
    assert result is None, "Should be None for cache miss"
    
    # Test 2: Cache set
    print("\n📋 Test 2: Cache set")
    success = cache.set(
        "How many universities in Dhaka?", 
        "institutions",
        "Found 5 universities",
        0.95,
        0.05
    )
    print(f"Set success: {success}")
    assert success, "Cache set should succeed"
    
    # Test 3: Cache hit
    print("\n📋 Test 3: Cache hit")
    result = cache.get("How many universities in Dhaka?", "institutions")
    print(f"Result: {result}")
    assert result is not None, "Should get cached result"
    assert result['cached'] == True, "Should be marked as cached"
    assert result['hit_count'] >= 1, "Should have at least 1 hit"
    
    # Test 4: Second cache hit
    print("\n📋 Test 4: Second cache hit")
    result = cache.get("How many universities in Dhaka?", "institutions")
    print(f"Hit count: {result['hit_count']}")
    assert result['hit_count'] >= 2, "Should have at least 2 hits"
    
    # Test 5: Cache stats
    print("\n📋 Test 5: Cache stats")
    stats = cache.get_stats()
    print(f"Stats: {stats}")
    assert stats['total_entries'] == 1, "Should have 1 entry"
    assert stats['valid_entries'] == 1, "Should have 1 valid entry"
    
    # Test 6: Cache invalidation
    print("\n📋 Test 6: Cache invalidation")
    success = cache.invalidate("How many universities in Dhaka?", "institutions")
    print(f"Invalidate success: {success}")
    assert success, "Invalidation should succeed"
    
    # Verify cache miss after invalidation
    result = cache.get("How many universities in Dhaka?", "institutions")
    assert result is None, "Should be None after invalidation"
    
    print("\n✅ All cache tests passed!")

if __name__ == "__main__":
    test_cache_manager()
