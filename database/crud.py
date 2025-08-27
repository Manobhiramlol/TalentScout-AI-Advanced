"""
CRUD operations for TalentScout AI database
Create, Read, Update, Delete operations for all database entities
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .database import get_db_connection, execute_query, execute_update

logger = logging.getLogger(__name__)

class MessageCRUD:
    """CRUD operations for messages"""
    
    @staticmethod
    def create_message(session_id: str, message_id: int, role: str, content: str, 
                      timestamp: str, stage: str) -> bool:
        """Create new message"""
        query = '''
            INSERT INTO messages (session_id, message_id, role, content, timestamp, stage)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        return execute_update(query, (session_id, message_id, role, content, timestamp, stage))
    
    @staticmethod
    def get_messages(session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session"""
        query = '''
            SELECT message_id, role, content, timestamp, stage 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY message_id ASC
        '''
        result = execute_query(query, (session_id,))
        return result if result else []
    
    @staticmethod
    def get_message_count(session_id: str) -> int:
        """Get total message count for session"""
        query = 'SELECT COUNT(*) as count FROM messages WHERE session_id = ?'
        result = execute_query(query, (session_id,))
        return result[0]['count'] if result else 0
    
    @staticmethod
    def delete_messages(session_id: str) -> bool:
        """Delete all messages for a session"""
        query = 'DELETE FROM messages WHERE session_id = ?'
        return execute_update(query, (session_id,))

class CandidateCRUD:
    """CRUD operations for candidates"""
    
    @staticmethod
    def create_candidate(session_id: str, candidate_data: Dict[str, Any]) -> bool:
        """Create or update candidate"""
        query = '''
            INSERT OR REPLACE INTO candidates 
            (session_id, name, email, phone, experience, position, tech_stack, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        tech_stack_json = json.dumps(candidate_data.get('tech_stack', []))
        
        return execute_update(query, (
            session_id,
            candidate_data.get('name', ''),
            candidate_data.get('email', ''),
            candidate_data.get('phone', ''),
            candidate_data.get('experience', ''),
            candidate_data.get('position', ''),
            tech_stack_json,
            datetime.now().isoformat()
        ))
    
    @staticmethod
    def get_candidate(session_id: str) -> Dict[str, Any]:
        """Get candidate by session ID"""
        query = 'SELECT * FROM candidates WHERE session_id = ?'
        result = execute_query(query, (session_id,))
        
        if result:
            candidate = result[0]
            # Parse tech_stack JSON
            if candidate.get('tech_stack'):
                try:
                    candidate['tech_stack'] = json.loads(candidate['tech_stack'])
                except json.JSONDecodeError:
                    candidate['tech_stack'] = []
            else:
                candidate['tech_stack'] = []
            return dict(candidate)
        
        return {}
    
    @staticmethod
    def update_candidate_field(session_id: str, field: str, value: Any) -> bool:
        """Update specific candidate field"""
        if field == 'tech_stack':
            value = json.dumps(value)
        
        query = f'UPDATE candidates SET {field} = ?, updated_at = ? WHERE session_id = ?'
        return execute_update(query, (value, datetime.now().isoformat(), session_id))
    
    @staticmethod
    def get_all_candidates() -> List[Dict[str, Any]]:
        """Get all candidates"""
        query = 'SELECT * FROM candidates ORDER BY created_at DESC'
        result = execute_query(query)
        
        if result:
            for candidate in result:
                if candidate.get('tech_stack'):
                    try:
                        candidate['tech_stack'] = json.loads(candidate['tech_stack'])
                    except json.JSONDecodeError:
                        candidate['tech_stack'] = []
        
        return result if result else []

class SessionCRUD:
    """CRUD operations for interview sessions"""
    
    @staticmethod
    def create_session(session_id: str) -> bool:
        """Create new interview session"""
        query = '''
            INSERT OR REPLACE INTO interview_sessions 
            (session_id, current_stage, start_time, status)
            VALUES (?, ?, ?, ?)
        '''
        return execute_update(query, (session_id, 'greeting', datetime.now().isoformat(), 'active'))
    
    @staticmethod
    def update_session_stage(session_id: str, stage: str, progress: int = None) -> bool:
        """Update session stage and progress"""
        if progress is not None:
            query = '''
                UPDATE interview_sessions 
                SET current_stage = ?, progress_percentage = ?
                WHERE session_id = ?
            '''
            return execute_update(query, (stage, progress, session_id))
        else:
            query = '''
                UPDATE interview_sessions 
                SET current_stage = ?
                WHERE session_id = ?
            '''
            return execute_update(query, (stage, session_id))
    
    @staticmethod
    def increment_ai_questions(session_id: str) -> bool:
        """Increment AI questions generated count"""
        query = '''
            UPDATE interview_sessions 
            SET ai_questions_generated = ai_questions_generated + 1
            WHERE session_id = ?
        '''
        return execute_update(query, (session_id,))
    
    @staticmethod
    def get_session(session_id: str) -> Dict[str, Any]:
        """Get session by ID"""
        query = 'SELECT * FROM interview_sessions WHERE session_id = ?'
        result = execute_query(query, (session_id,))
        return dict(result[0]) if result else {}
    
    @staticmethod
    def complete_session(session_id: str) -> bool:
        """Mark session as completed"""
        query = '''
            UPDATE interview_sessions 
            SET status = ?, end_time = ?, progress_percentage = 100
            WHERE session_id = ?
        '''
        return execute_update(query, ('completed', datetime.now().isoformat(), session_id))

class AnalyticsCRUD:
    """CRUD operations for analytics"""
    
    @staticmethod
    def log_event(session_id: str, event_type: str, event_data: Dict[str, Any] = None) -> bool:
        """Log analytics event"""
        query = '''
            INSERT INTO analytics (session_id, event_type, event_data)
            VALUES (?, ?, ?)
        '''
        
        event_data_json = json.dumps(event_data) if event_data else None
        return execute_update(query, (session_id, event_type, event_data_json))
    
    @staticmethod
    def get_session_analytics(session_id: str) -> List[Dict[str, Any]]:
        """Get analytics for specific session"""
        query = '''
            SELECT event_type, event_data, timestamp 
            FROM analytics 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        '''
        result = execute_query(query, (session_id,))
        
        if result:
            for event in result:
                if event.get('event_data'):
                    try:
                        event['event_data'] = json.loads(event['event_data'])
                    except json.JSONDecodeError:
                        event['event_data'] = {}
        
        return result if result else []
    
    @staticmethod
    def get_system_analytics() -> Dict[str, Any]:
        """Get system-wide analytics"""
        analytics = {}
        
        # Event type distribution
        query = '''
            SELECT event_type, COUNT(*) as count 
            FROM analytics 
            GROUP BY event_type 
            ORDER BY count DESC
        '''
        result = execute_query(query)
        analytics['event_distribution'] = result if result else []
        
        # Daily activity
        query = '''
            SELECT DATE(timestamp) as date, COUNT(*) as events 
            FROM analytics 
            WHERE timestamp > date('now', '-7 days')
            GROUP BY DATE(timestamp) 
            ORDER BY date DESC
        '''
        result = execute_query(query)
        analytics['daily_activity'] = result if result else []
        
        return analytics

# Convenience instances
message_crud = MessageCRUD()
candidate_crud = CandidateCRUD()
session_crud = SessionCRUD()
analytics_crud = AnalyticsCRUD()
