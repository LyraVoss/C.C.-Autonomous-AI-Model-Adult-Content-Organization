from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import random
from .models import DigitalCreator, Subscriber, SubscriptionTier, Niche

class InteractionManager:
    def __init__(self):
        self.conversation_history: Dict[str, List[Dict]] = {}  # user_id: messages
        self.loyalty_points: Dict[str, int] = {}  # user_id: points

    def generate_response(self, creator: DigitalCreator, user_message: str, user_id: str, context: Dict = {}) -> str:
        """Generate a personalized response based on creator's personality and user history"""
        # Get conversation history
        history = self.conversation_history.get(user_id, [])

        # Check subscriber status
        subscriber = next((s for s in creator.subscribers if s.id == user_id), None)
        is_subscriber = subscriber is not None
        tier = subscriber.tier if subscriber else SubscriptionTier.FREE

        # Generate response based on personality and context
        response = self._craft_response(creator, user_message, history, is_subscriber, tier, context)

        # Update conversation history
        message_record = {
            'timestamp': datetime.now(),
            'user_message': user_message,
            'creator_response': response,
            'context': context
        }
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        self.conversation_history[user_id].append(message_record)

        # Award loyalty points for interaction
        self._award_loyalty_points(user_id, 1)

        return response

    def _craft_response(self, creator: DigitalCreator, message: str, history: List[Dict],
                       is_subscriber: bool, tier: SubscriptionTier, context: Dict) -> str:
        """Craft a response based on various factors"""
        message_lower = message.lower()

        # Determine intent
        intent = self._analyze_intent(message_lower)

        # Get personality-based response style
        personality_modifier = self._get_personality_modifier(creator.personality_traits)

        # Base response templates
        responses = self._get_response_templates(creator, intent)

        # Select and personalize response
        base_response = random.choice(responses[intent])

        # Apply personality modifier
        response = personality_modifier(base_response)

        # Add subscriber-specific content
        if is_subscriber and tier != SubscriptionTier.FREE:
            response += f" Thanks for being a {tier.value} member! 💕"

        return response

    def _analyze_intent(self, message: str) -> str:
        """Analyze message intent"""
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening']
        flirty_words = ['sexy', 'hot', 'naughty', 'dirty', 'wet', 'hard', 'want']
        content_words = ['custom', 'request', 'want', 'make', 'create', 'video', 'photo']
        subscription_words = ['subscribe', 'premium', 'vip', 'join', 'membership']

        if any(word in message for word in greetings):
            return 'greeting'
        elif any(word in message for word in flirty_words):
            return 'flirty'
        elif any(word in message for word in content_words):
            return 'content_request'
        elif any(word in message for word in subscription_words):
            return 'subscription'
        else:
            return 'flirty'  # Default

    def _get_response_templates(self, creator: DigitalCreator, intent: str) -> Dict[str, List[str]]:
        """Get response templates based on creator niche"""
        base_templates = {
            'greeting': [
                f"Hey there! {creator.name} here, ready to make your day amazing 💋",
                f"Welcome back! I've been thinking about you 😘",
                f"Hello gorgeous! What can I do for you today?"
            ],
            'flirty': [
                f"Oh, you're making me blush! Tell me more about what you like 😉",
                f"Mmm, I love hearing that. What else turns you on?",
                f"You're so tempting... I might have to show you something special"
            ],
            'content_request': [
                f"I'd love to create something just for you! What did you have in mind?",
                f"Tell me your fantasies, and I'll make them come to life 🔥",
                f"Custom content? I'm all yours. Describe your perfect scenario"
            ],
            'subscription': [
                f"Want exclusive access to my premium content? Subscribe now! 💎",
                f"Join my VIP club for personalized experiences and direct messages",
                f"Unlock all my secrets with a subscription - you won't regret it!"
            ]
        }

        # Customize based on niche
        if creator.niche == Niche.BDSM:
            base_templates['flirty'].extend([
                "I can see you're into the more... intense side of things 😈",
                "Tell me your limits, and I'll push them just right"
            ])

        return base_templates

    def _get_personality_modifier(self, traits: List[str]) -> Callable[[str], str]:
        """Get a function to modify responses based on personality"""
        def modifier(response: str) -> str:
            if 'confident' in traits:
                response = response.replace('maybe', 'definitely').replace('might', 'will')
            if 'playful' in traits:
                if random.random() < 0.3:
                    response += " 😜"
            if 'dominant' in traits.lower():
                response = response.replace('please', 'beg')
            return response
        return modifier

    def send_automated_dm(self, creator: DigitalCreator, user_id: str, message_type: str):
        """Send automated direct messages"""
        messages = {
            'welcome': f"Welcome to my world! I'm {creator.name}, and I'm here to fulfill your fantasies.",
            'inactive': f"Hey! I've missed you. Come back and let's have some fun together 😘",
            'new_content': f"New content just dropped! Check it out and let me know what you think 🔥",
            'birthday': f"Happy birthday! Here's a special gift just for you 🎁",
            'anniversary': f"It's been a year since you joined! Thank you for being amazing 💋"
        }

        if message_type in messages:
            # In a real implementation, this would send via platform APIs
            print(f"DM to {user_id} from {creator.name}: {messages[message_type]}")

    def manage_loyalty_program(self, creator: DigitalCreator):
        """Manage loyalty points and rewards"""
        for user_id, points in self.loyalty_points.items():
            if points >= 100:  # Threshold for reward
                self.send_automated_dm(creator, user_id, 'loyalty_reward')
                self.loyalty_points[user_id] -= 100  # Reset or deduct

    def _award_loyalty_points(self, user_id: str, points: int):
        """Award loyalty points to a user"""
        if user_id not in self.loyalty_points:
            self.loyalty_points[user_id] = 0
        self.loyalty_points[user_id] += points

    def get_user_insights(self, user_id: str) -> Dict:
        """Get insights about a user's interaction patterns"""
        history = self.conversation_history.get(user_id, [])
        if not history:
            return {}

        # Analyze preferences
        messages = [h['user_message'].lower() for h in history]
        preferences = {
            'mentions_bondage': any('bondage' in msg or 'tie' in msg for msg in messages),
            'mentions_roleplay': any('roleplay' in msg or 'role' in msg for msg in messages),
            'mentions_dominant': any('dominant' in msg or 'dom' in msg for msg in messages),
            'mentions_submissive': any('submissive' in msg or 'sub' in msg for msg in messages),
        }

        return {
            'total_interactions': len(history),
            'loyalty_points': self.loyalty_points.get(user_id, 0),
            'preferences': preferences,
            'last_interaction': history[-1]['timestamp'] if history else None
        }

    def trigger_personalized_content(self, creator: DigitalCreator, user_id: str):
        """Trigger creation of personalized content based on user preferences"""
        insights = self.get_user_insights(user_id)
        if not insights:
            return

        # Generate content based on preferences
        theme = "general"
        if insights['preferences']['mentions_bondage']:
            theme = "bondage adventure"
        elif insights['preferences']['mentions_roleplay']:
            theme = "roleplay scenario"
        elif insights['preferences']['mentions_dominant']:
            theme = "dominant encounter"
        elif insights['preferences']['mentions_submissive']:
            theme = "submissive experience"

        # In a real implementation, this would trigger content generation
        print(f"Generating personalized content for {user_id}: {theme}")

    def handle_moderation(self, creator: DigitalCreator, message: str, user_id: str) -> bool:
        """Moderate messages for inappropriate content"""
        banned_words = ['spam', 'scam', 'inappropriate_word']  # Define banned words
        if any(word in message.lower() for word in banned_words):
            # Log and potentially ban user
            print(f"Moderation alert: Banned word in message from {user_id}")
            return False  # Block message
        return True  # Allow message