from typing import Dict, List, Optional
from datetime import datetime, timedelta
import stripe  # Assuming Stripe for payments
from .models import DigitalCreator, Subscriber, SubscriptionTier

class MonetizationManager:
    def __init__(self, stripe_secret_key: str):
        stripe.api_key = stripe_secret_key
        self.creators_revenue: Dict[str, float] = {}

    def create_subscription_product(self, creator: DigitalCreator, tier: SubscriptionTier) -> str:
        """Create a Stripe product for a subscription tier"""
        tier_info = creator.subscription_tiers[tier]

        product = stripe.Product.create(
            name=f"{creator.name} - {tier.value.title()} Subscription",
            description=tier_info.get('description', f"Access to {creator.name}'s {tier.value} content"),
        )

        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(tier_info['price'] * 100),  # Convert to cents
            currency='usd',
            recurring={'interval': 'month'},
        )

        return price.id

    def process_subscription(self, creator: DigitalCreator, subscriber_email: str, tier: SubscriptionTier, payment_method_id: str) -> Subscriber:
        """Process a new subscription payment"""
        tier_info = creator.subscription_tiers[tier]
        price_id = tier_info.get('stripe_price_id')

        if not price_id:
            price_id = self.create_subscription_product(creator, tier)
            tier_info['stripe_price_id'] = price_id

        # Create Stripe subscription
        subscription = stripe.Subscription.create(
            customer_email=subscriber_email,
            items=[{'price': price_id}],
            default_payment_method=payment_method_id,
        )

        # Create subscriber record
        subscriber = Subscriber(
            id=subscription.customer,
            username=subscriber_email.split('@')[0],
            email=subscriber_email,
            tier=tier,
            subscribed_at=datetime.now(),
            last_active=datetime.now()
        )

        creator.add_subscriber(subscriber)
        self.update_revenue(creator.id, tier_info['price'])

        return subscriber

    def process_one_time_purchase(self, creator: DigitalCreator, content_id: str, amount: float, payment_method_id: str) -> bool:
        """Process pay-per-view or tip payment"""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency='usd',
                payment_method=payment_method_id,
                confirm=True,
                description=f"Purchase from {creator.name}: {content_id}"
            )

            if payment_intent.status == 'succeeded':
                self.update_revenue(creator.id, amount)
                return True
            return False
        except Exception as e:
            print(f"Payment failed: {e}")
            return False

    def update_revenue(self, creator_id: str, amount: float):
        """Update creator's revenue tracking"""
        if creator_id not in self.creators_revenue:
            self.creators_revenue[creator_id] = 0
        self.creators_revenue[creator_id] += amount

    def get_creator_revenue(self, creator_id: str) -> float:
        """Get total revenue for a creator"""
        return self.creators_revenue.get(creator_id, 0)

    def calculate_payout(self, creator: DigitalCreator, period_days: int = 30) -> float:
        """Calculate payout amount for a creator (after platform fees)"""
        total_revenue = self.get_creator_revenue(creator.id)
        platform_fee = 0.2  # 20% platform fee
        return total_revenue * (1 - platform_fee)

    def cancel_subscription(self, creator: DigitalCreator, subscriber_id: str):
        """Cancel a subscriber's subscription"""
        # In a real implementation, this would cancel the Stripe subscription
        creator.remove_subscriber(subscriber_id)

    def get_subscription_analytics(self, creator: DigitalCreator) -> Dict:
        """Get subscription analytics for a creator"""
        subscribers = creator.subscribers
        tier_counts = {}
        for tier in SubscriptionTier:
            tier_counts[tier.value] = len([s for s in subscribers if s.tier == tier])

        return {
            'total_subscribers': len(subscribers),
            'tier_breakdown': tier_counts,
            'monthly_revenue': self.get_creator_revenue(creator.id),
            'average_revenue_per_subscriber': self.get_creator_revenue(creator.id) / max(len(subscribers), 1)
        }