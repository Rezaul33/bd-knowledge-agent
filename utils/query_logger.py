"""
Query Logger - Comprehensive logging system for all queries and responses
"""

import sqlite3
import json
import time
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.database import DatabaseManager

class QueryLogger:
    """SQLite-based query logging system with comprehensive tracking"""
    
    def __init__(self, log_db_path: str = None):
        self.log_db_path = log_db_path or Config.LOG_DB
        self._initialize_log_db()
    
    def _initialize_log_db(self):
        """Initialize log database with comprehensive schema"""
        conn = DatabaseManager.create_connection(self.log_db_path)
        try:
            cursor = conn.cursor()
            
            # Create main query log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    query_text TEXT NOT NULL,
                    query_type TEXT,
                    tool_used TEXT NOT NULL,
                    routing_confidence REAL,
                    result_confidence REAL,
                    execution_time REAL,
                    response_text TEXT,
                    response_length INTEGER,
                    cached BOOLEAN DEFAULT FALSE,
                    cache_hits INTEGER DEFAULT 0,
                    fallback_used BOOLEAN DEFAULT FALSE,
                    sql_executed BOOLEAN DEFAULT FALSE,
                    sql_query TEXT,
                    error_occurred BOOLEAN DEFAULT FALSE,
                    error_message TEXT,
                    user_ip TEXT,
                    user_agent TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON query_log(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON query_log(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tool_used ON query_log(tool_used)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_type ON query_log(query_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cached ON query_log(cached)')
            
            # Create aggregated statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    total_queries INTEGER DEFAULT 0,
                    unique_sessions INTEGER DEFAULT 0,
                    avg_execution_time REAL DEFAULT 0,
                    avg_confidence REAL DEFAULT 0,
                    cache_hit_rate REAL DEFAULT 0,
                    error_rate REAL DEFAULT 0,
                    tool_distribution TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        finally:
            conn.close()
    
    def log_query(self, query_data: Dict[str, Any]) -> bool:
        """
        Log a complete query with all metadata
        
        Args:
            query_data: Dictionary containing all query information
            
        Returns:
            True if logged successfully, False otherwise
        """
        conn = DatabaseManager.create_connection(self.log_db_path)
        try:
            cursor = conn.cursor()
            
            # Extract and prepare data
            session_id = query_data.get('session_id', 'unknown')
            timestamp = query_data.get('timestamp', datetime.now().isoformat())
            query_text = query_data.get('query', '')
            query_type = query_data.get('classification', {}).get('question_type', 'general')
            tool_used = query_data.get('tool_used', 'unknown')
            routing_confidence = query_data.get('routing_confidence', 0.0)
            result_confidence = query_data.get('result_confidence', 0.0)
            execution_time = query_data.get('execution_time', 0.0)
            response_text = query_data.get('response', '')
            response_length = len(response_text)
            cached = query_data.get('cached', False)
            cache_hits = query_data.get('cache_hits', 0)
            fallback_used = query_data.get('fallback_used', False)
            sql_executed = tool_used.lower() != 'web_search'
            
            # Extract SQL if available
            sql_query = None
            if 'classification' in query_data and 'sql_query' in query_data['classification']:
                sql_query = query_data['classification']['sql_query']
            
            error_occurred = not query_data.get('success', True)
            error_message = query_data.get('error', None)
            
            # Store additional metadata as JSON
            metadata = {
                'classification': query_data.get('classification', {}),
                'cache_info': {
                    'cached': cached,
                    'cache_hits': cache_hits
                }
            }
            
            # Insert log entry
            cursor.execute('''
                INSERT INTO query_log 
                (session_id, timestamp, query_text, query_type, tool_used, 
                 routing_confidence, result_confidence, execution_time, 
                 response_text, response_length, cached, cache_hits, 
                 fallback_used, sql_executed, sql_query, error_occurred, 
                 error_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, timestamp, query_text, query_type, tool_used,
                routing_confidence, result_confidence, execution_time,
                response_text, response_length, cached, cache_hits,
                fallback_used, sql_executed, sql_query, error_occurred,
                error_message, json.dumps(metadata)
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Logging error: {e}")
            return False
        finally:
            conn.close()
    
    def get_query_history(self, session_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get query history with optional session filtering"""
        conn = DatabaseManager.create_connection(self.log_db_path)
        try:
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT * FROM query_log 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (session_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM query_log 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result_dict = dict(zip(columns, row))
                # Parse metadata JSON
                if result_dict.get('metadata'):
                    try:
                        result_dict['metadata'] = json.loads(result_dict['metadata'])
                    except:
                        result_dict['metadata'] = {}
                results.append(result_dict)
            
            return results
            
        finally:
            conn.close()
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive statistics for the last N days"""
        conn = DatabaseManager.create_connection(self.log_db_path)
        try:
            cursor = conn.cursor()
            
            # Date filter
            date_filter = f"date('now', '-{days} days')"
            
            # Basic stats
            cursor.execute(f'''
                SELECT 
                    COUNT(*) as total_queries,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    AVG(execution_time) as avg_execution_time,
                    AVG(result_confidence) as avg_confidence,
                    SUM(CASE WHEN cached THEN 1 ELSE 0 END) as cached_queries,
                    SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END) as error_queries
                FROM query_log 
                WHERE timestamp >= {date_filter}
            ''')
            
            basic_stats = cursor.fetchone()
            
            # Tool distribution
            cursor.execute(f'''
                SELECT tool_used, COUNT(*) as count
                FROM query_log 
                WHERE timestamp >= {date_filter}
                GROUP BY tool_used
                ORDER BY count DESC
            ''')
            
            tool_dist = cursor.fetchall()
            
            # Query type distribution
            cursor.execute(f'''
                SELECT query_type, COUNT(*) as count
                FROM query_log 
                WHERE timestamp >= {date_filter}
                GROUP BY query_type
                ORDER BY count DESC
            ''')
            
            query_type_dist = cursor.fetchall()
            
            # Hourly distribution
            cursor.execute(f'''
                SELECT 
                    CASE 
                        WHEN CAST(strftime('%H', timestamp) AS INTEGER) < 6 THEN 'Night'
                        WHEN CAST(strftime('%H', timestamp) AS INTEGER) < 12 THEN 'Morning'
                        WHEN CAST(strftime('%H', timestamp) AS INTEGER) < 18 THEN 'Afternoon'
                        ELSE 'Evening'
                    END as time_period,
                    COUNT(*) as count
                FROM query_log 
                WHERE timestamp >= {date_filter}
                GROUP BY time_period
                ORDER BY count DESC
            ''')
            
            hourly_dist = cursor.fetchall()
            
            # Calculate derived metrics
            total_queries = basic_stats[0] or 1
            cache_hit_rate = (basic_stats[4] / total_queries) * 100 if total_queries > 0 else 0
            error_rate = (basic_stats[5] / total_queries) * 100 if total_queries > 0 else 0
            
            return {
                'period_days': days,
                'total_queries': basic_stats[0] or 0,
                'unique_sessions': basic_stats[1] or 0,
                'avg_execution_time': round(basic_stats[2] or 0, 3),
                'avg_confidence': round(basic_stats[3] or 0, 2),
                'cached_queries': basic_stats[4] or 0,
                'error_queries': basic_stats[5] or 0,
                'cache_hit_rate': round(cache_hit_rate, 2),
                'error_rate': round(error_rate, 2),
                'tool_distribution': [
                    {'tool': tool, 'count': count, 'percentage': round((count/total_queries)*100, 1)}
                    for tool, count in tool_dist
                ],
                'query_type_distribution': [
                    {'type': qtype, 'count': count, 'percentage': round((count/total_queries)*100, 1)}
                    for qtype, count in query_type_dist
                ],
                'time_distribution': [
                    {'period': period, 'count': count, 'percentage': round((count/total_queries)*100, 1)}
                    for period, count in hourly_dist
                ]
            }
            
        finally:
            conn.close()
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get detailed summary for a specific session"""
        conn = DatabaseManager.create_connection(self.log_db_path)
        try:
            cursor = conn.cursor()
            
            # Session basic stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_queries,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time,
                    AVG(execution_time) as avg_execution_time,
                    AVG(result_confidence) as avg_confidence,
                    SUM(CASE WHEN cached THEN 1 ELSE 0 END) as cached_queries,
                    SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END) as error_queries
                FROM query_log 
                WHERE session_id = ?
            ''', (session_id,))
            
            session_stats = cursor.fetchone()
            
            # Session queries
            cursor.execute('''
                SELECT query_text, tool_used, execution_time, result_confidence, cached
                FROM query_log 
                WHERE session_id = ?
                ORDER BY timestamp
            ''', (session_id,))
            
            queries = cursor.fetchall()
            
            if not session_stats[0]:
                return {'error': 'Session not found'}
            
            total_queries = session_stats[0]
            cache_hit_rate = (session_stats[5] / total_queries) * 100 if total_queries > 0 else 0
            error_rate = (session_stats[6] / total_queries) * 100 if total_queries > 0 else 0
            
            return {
                'session_id': session_id,
                'total_queries': total_queries,
                'start_time': session_stats[1],
                'end_time': session_stats[2],
                'avg_execution_time': round(session_stats[3] or 0, 3),
                'avg_confidence': round(session_stats[4] or 0, 2),
                'cached_queries': session_stats[5] or 0,
                'error_queries': session_stats[6] or 0,
                'cache_hit_rate': round(cache_hit_rate, 2),
                'error_rate': round(error_rate, 2),
                'queries': [
                    {
                        'query': q[0],
                        'tool': q[1],
                        'execution_time': q[2],
                        'confidence': q[3],
                        'cached': bool(q[4])
                    }
                    for q in queries
                ]
            }
            
        finally:
            conn.close()
    
    def clear_old_logs(self, days: int = 30) -> int:
        """Clear logs older than specified days"""
        conn = DatabaseManager.create_connection(self.log_db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(f'''
                DELETE FROM query_log 
                WHERE timestamp < date('now', '-{days} days')
            ''')
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def export_logs(self, output_file: str, format: str = 'json') -> bool:
        """Export logs to file"""
        try:
            logs = self.get_query_history(limit=10000)  # Get recent logs
            
            if format.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, default=str)
            elif format.lower() == 'csv':
                import csv
                if logs:
                    with open(output_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                        writer.writeheader()
                        writer.writerows(logs)
            
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

# Test the query logger
def test_query_logger():
    """Test query logger functionality"""
    logger = QueryLogger("logs/test_log.db")
    
    print("🧪 Testing Query Logger...")
    
    # Test 1: Log a query
    print("\n📋 Test 1: Log a query")
    test_query_data = {
        'session_id': 'test_session_123',
        'timestamp': datetime.now().isoformat(),
        'query': 'How many universities in Dhaka?',
        'tool_used': 'InstitutionsDBTool',
        'routing_confidence': 0.95,
        'result_confidence': 0.95,
        'execution_time': 0.05,
        'response': 'Found 5 universities matching your criteria.',
        'cached': False,
        'cache_hits': 0,
        'fallback_used': False,
        'success': True,
        'classification': {
            'question_type': 'count',
            'primary_tool': 'institutions'
        }
    }
    
    success = logger.log_query(test_query_data)
    print(f"Log success: {success}")
    assert success, "Logging should succeed"
    
    # Test 2: Get query history
    print("\n📋 Test 2: Get query history")
    history = logger.get_query_history(limit=5)
    print(f"History entries: {len(history)}")
    assert len(history) > 0, "Should have history entries"
    
    # Test 3: Get statistics
    print("\n📋 Test 3: Get statistics")
    stats = logger.get_statistics(days=7)
    print(f"Total queries: {stats['total_queries']}")
    assert stats['total_queries'] > 0, "Should have queries in stats"
    
    # Test 4: Get session summary
    print("\n📋 Test 4: Get session summary")
    session_summary = logger.get_session_summary('test_session_123')
    print(f"Session queries: {session_summary['total_queries']}")
    assert session_summary['total_queries'] > 0, "Should have session queries"
    
    print("\n✅ All logger tests passed!")

if __name__ == "__main__":
    test_query_logger()
