from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from modles.message import Message, Conversation
from modles.user import User
from utils.serializers import serialize_doc

messages = Blueprint('messages', __name__)


@messages.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get all conversations for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get all conversations
        conversations = Conversation.get_user_conversations(current_user_id)
        
        result = []
        for conv in conversations:
            # Get the other participant
            other_participant_id = Conversation.get_other_participant(
                str(conv['_id']), 
                current_user_id
            )
            
            if not other_participant_id:
                continue
            
            # Get other participant details
            other_user = User.find_by_id(str(other_participant_id))
            if not other_user:
                continue
            
            # Get unread count
            unread_count = Conversation.get_unread_count_by_conversation(
                str(conv['_id']), 
                current_user_id
            )
            
            # Format last message time
            last_message_time = conv.get('last_message_time')
            time_ago = format_time_ago(last_message_time) if last_message_time else 'No messages'
            
            result.append({
                'id': str(conv['_id']),
                'name': other_user.get('fullName', 'Unknown User'),
                'avatar': other_user.get('avatar', 'https://via.placeholder.com/40'),
                'status': 'Online',  # Can be enhanced with real-time status
                'unread': unread_count,
                'lastMessageTime': time_ago,
                'lastMessage': conv.get('last_message', 'No messages yet'),
                'participantId': str(other_participant_id),
                'participantRole': other_user.get('role', 'student')
            })
        
        return jsonify({
            'success': True,
            'conversations': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching conversations: {str(e)}'
        }), 500


@messages.route('/conversation/<conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation_messages(conversation_id):
    """Get all messages in a conversation"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user is part of the conversation
        conversation = Conversation.get_conversation_by_id(conversation_id)
        if not conversation:
            return jsonify({
                'success': False,
                'message': 'Conversation not found'
            }), 404
        
        participants = [str(p) for p in conversation.get('participants', [])]
        if current_user_id not in participants:
            return jsonify({
                'success': False,
                'message': 'Unauthorized access to conversation'
            }), 403
        
        # Get messages
        messages_list = Message.get_conversation_messages(conversation_id)
        
        # Mark messages as read
        Message.mark_conversation_as_read(conversation_id, current_user_id)
        
        # Format messages
        formatted_messages = []
        for msg in messages_list:
            sender_id = str(msg.get('sender_id'))
            formatted_messages.append({
                'id': str(msg['_id']),
                'sender': 'user' if sender_id == current_user_id else 'recipient',
                'senderId': sender_id,
                'text': msg.get('text', ''),
                'time': msg.get('timestamp').strftime('%I:%M %p') if msg.get('timestamp') else '',
                'date': format_message_date(msg.get('timestamp')) if msg.get('timestamp') else 'Today',
                'isRead': msg.get('is_read', False)
            })
        
        # Get other participant info
        other_participant_id = Conversation.get_other_participant(
            conversation_id, 
            current_user_id
        )
        other_user = User.find_by_id(str(other_participant_id)) if other_participant_id else None
        
        return jsonify({
            'success': True,
            'messages': formatted_messages,
            'participant': {
                'id': str(other_participant_id) if other_participant_id else None,
                'name': other_user.get('fullName', 'Unknown User') if other_user else 'Unknown User',
                'avatar': other_user.get('avatar', 'https://via.placeholder.com/40') if other_user else 'https://via.placeholder.com/40',
                'status': 'Online',
                'role': other_user.get('role', 'student') if other_user else 'student'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching messages: {str(e)}'
        }), 500


@messages.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    """Send a new message"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        conversation_id = data.get('conversationId')
        text = data.get('text', '').strip()
        
        if not conversation_id or not text:
            return jsonify({
                'success': False,
                'message': 'Conversation ID and message text are required'
            }), 400
        
        # Verify user is part of the conversation
        conversation = Conversation.get_conversation_by_id(conversation_id)
        if not conversation:
            return jsonify({
                'success': False,
                'message': 'Conversation not found'
            }), 404
        
        participants = [str(p) for p in conversation.get('participants', [])]
        if current_user_id not in participants:
            return jsonify({
                'success': False,
                'message': 'Unauthorized access to conversation'
            }), 403
        
        # Get recipient ID (the other participant)
        recipient_id = None
        for participant_id in participants:
            if participant_id != current_user_id:
                recipient_id = participant_id
                break
        
        if not recipient_id:
            return jsonify({
                'success': False,
                'message': 'Recipient not found'
            }), 400
        
        # Create message
        message_id = Message.create_message(
            sender_id=current_user_id,
            recipient_id=recipient_id,
            conversation_id=conversation_id,
            text=text
        )
        
        # Update conversation's last message
        Conversation.update_last_message(conversation_id, text)
        
        # Get the created message
        message = mongo.db.messages.find_one({'_id': ObjectId(message_id)})
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'data': {
                'id': str(message['_id']),
                'sender': 'user',
                'senderId': current_user_id,
                'text': message.get('text', ''),
                'time': message.get('timestamp').strftime('%I:%M %p') if message.get('timestamp') else '',
                'date': format_message_date(message.get('timestamp')) if message.get('timestamp') else 'Today',
                'isRead': False
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error sending message: {str(e)}'
        }), 500


@messages.route('/conversation/create', methods=['POST'])
@jwt_required()
def create_conversation():
    """Create a new conversation"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        recipient_id = data.get('recipientId')
        
        if not recipient_id:
            return jsonify({
                'success': False,
                'message': 'Recipient ID is required'
            }), 400
        
        # Verify recipient exists
        recipient = User.find_by_id(recipient_id)
        if not recipient:
            return jsonify({
                'success': False,
                'message': 'Recipient not found'
            }), 404
        
        # Create conversation
        conversation_id = Conversation.create_conversation(
            participant_ids=[current_user_id, recipient_id],
            created_by=current_user_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Conversation created successfully',
            'conversationId': conversation_id,
            'participant': {
                'id': recipient_id,
                'name': recipient.get('fullName', 'Unknown User'),
                'avatar': recipient.get('avatar', 'https://via.placeholder.com/40'),
                'role': recipient.get('role', 'student')
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating conversation: {str(e)}'
        }), 500


@messages.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get unread message count for current user"""
    try:
        current_user_id = get_jwt_identity()
        count = Message.get_unread_count(current_user_id)
        
        return jsonify({
            'success': True,
            'unreadCount': count
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching unread count: {str(e)}'
        }), 500


@messages.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    """Search for users to start a conversation with"""
    try:
        current_user_id = get_jwt_identity()
        search_query = request.args.get('q', '').strip()
        
        if not search_query:
            return jsonify({
                'success': False,
                'message': 'Search query is required'
            }), 400
        
        # Search for users by name or email
        from extensions import mongo
        users = mongo.db.users.find({
            '_id': {'$ne': ObjectId(current_user_id)},
            '$or': [
                {'fullName': {'$regex': search_query, '$options': 'i'}},
                {'email': {'$regex': search_query, '$options': 'i'}}
            ]
        }).limit(10)
        
        result = []
        for user in users:
            result.append({
                'id': str(user['_id']),
                'name': user.get('fullName', 'Unknown User'),
                'email': user.get('email', ''),
                'role': user.get('role', 'student'),
                'avatar': user.get('avatar', 'https://via.placeholder.com/40')
            })
        
        return jsonify({
            'success': True,
            'users': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching users: {str(e)}'
        }), 500


# Helper functions
def format_time_ago(timestamp):
    """Format timestamp to relative time"""
    if not timestamp:
        return 'Unknown'
    
    now = datetime.utcnow()
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'Just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes}m ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours}h ago'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days}d ago'
    else:
        return timestamp.strftime('%b %d')


def format_message_date(timestamp):
    """Format message date"""
    if not timestamp:
        return 'Today'
    
    now = datetime.utcnow()
    today = now.date()
    msg_date = timestamp.date()
    
    if msg_date == today:
        return 'Today'
    elif (today - msg_date).days == 1:
        return 'Yesterday'
    elif (today - msg_date).days < 7:
        return f'{(today - msg_date).days} days ago'
    else:
        return timestamp.strftime('%b %d, %Y')


# Import mongo for search_users function
from extensions import mongo
