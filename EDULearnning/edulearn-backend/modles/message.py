from bson import ObjectId
from datetime import datetime
from extensions import mongo

class Message:
    """Model for individual messages"""
    
    @staticmethod
    def create_message(sender_id, recipient_id, conversation_id, text):
        """Create a new message"""
        message_data = {
            'sender_id': ObjectId(sender_id),
            'recipient_id': ObjectId(recipient_id),
            'conversation_id': ObjectId(conversation_id),
            'text': text,
            'timestamp': datetime.utcnow(),
            'is_read': False,
            'created_at': datetime.utcnow()
        }
        result = mongo.db.messages.insert_one(message_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_conversation_messages(conversation_id, limit=100):
        """Get all messages in a conversation"""
        messages = mongo.db.messages.find({
            'conversation_id': ObjectId(conversation_id)
        }).sort('timestamp', 1).limit(limit)
        return list(messages)
    
    @staticmethod
    def mark_as_read(message_id):
        """Mark a message as read"""
        mongo.db.messages.update_one(
            {'_id': ObjectId(message_id)},
            {'$set': {'is_read': True}}
        )
    
    @staticmethod
    def mark_conversation_as_read(conversation_id, user_id):
        """Mark all messages in a conversation as read for a specific user"""
        mongo.db.messages.update_many(
            {
                'conversation_id': ObjectId(conversation_id),
                'recipient_id': ObjectId(user_id),
                'is_read': False
            },
            {'$set': {'is_read': True}}
        )
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread messages for a user"""
        count = mongo.db.messages.count_documents({
            'recipient_id': ObjectId(user_id),
            'is_read': False
        })
        return count


class Conversation:
    """Model for conversations between users"""
    
    @staticmethod
    def create_conversation(participant_ids, created_by):
        """Create a new conversation"""
        # Check if conversation already exists between these participants
        existing = mongo.db.conversations.find_one({
            'participants': {'$all': [ObjectId(pid) for pid in participant_ids]}
        })
        
        if existing:
            return str(existing['_id'])
        
        conversation_data = {
            'participants': [ObjectId(pid) for pid in participant_ids],
            'created_by': ObjectId(created_by),
            'created_at': datetime.utcnow(),
            'last_message': None,
            'last_message_time': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = mongo.db.conversations.insert_one(conversation_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_conversations(user_id):
        """Get all conversations for a user"""
        conversations = mongo.db.conversations.find({
            'participants': ObjectId(user_id)
        }).sort('last_message_time', -1)
        return list(conversations)
    
    @staticmethod
    def get_conversation_by_id(conversation_id):
        """Get a specific conversation"""
        return mongo.db.conversations.find_one({'_id': ObjectId(conversation_id)})
    
    @staticmethod
    def update_last_message(conversation_id, message_text):
        """Update the last message and timestamp for a conversation"""
        mongo.db.conversations.update_one(
            {'_id': ObjectId(conversation_id)},
            {
                '$set': {
                    'last_message': message_text,
                    'last_message_time': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }
        )
    
    @staticmethod
    def get_unread_count_by_conversation(conversation_id, user_id):
        """Get unread message count for a specific conversation"""
        count = mongo.db.messages.count_documents({
            'conversation_id': ObjectId(conversation_id),
            'recipient_id': ObjectId(user_id),
            'is_read': False
        })
        return count
    
    @staticmethod
    def get_other_participant(conversation_id, current_user_id):
        """Get the other participant in a conversation"""
        conversation = Conversation.get_conversation_by_id(conversation_id)
        if not conversation:
            return None
        
        participants = conversation.get('participants', [])
        for participant_id in participants:
            if str(participant_id) != str(current_user_id):
                return participant_id
        return None
