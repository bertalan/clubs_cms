"""Insert realistic demo notifications for demo_marco."""
import django
django.setup()

from apps.notifications.models import NotificationQueue
from apps.members.models import ClubUser
from django.utils import timezone
from datetime import timedelta

marco = ClubUser.objects.get(username="demo_marco")
now = timezone.now()

notifications = [
    {
        "notification_type": "event_reminder",
        "recipient": marco,
        "channel": "in_app",
        "title": "Reminder: Mandello del Lario Rally in 3 days",
        "body": (
            "The annual Mandello del Lario rally is coming up this weekend. "
            "Check the route and weather forecast. See you there."
        ),
        "url": "/en/events/",
        "status": "sent",
        "sent_at": now - timedelta(hours=2),
    },
    {
        "notification_type": "comment_reply",
        "recipient": marco,
        "channel": "email",
        "title": "Giulia replied to your comment",
        "body": (
            "Giulia Ferrara replied to your comment on Spring Kickoff 2026: "
            "Great idea Marco, let us organise a group departure from Milan."
        ),
        "url": "/en/news/",
        "status": "sent",
        "sent_at": now - timedelta(hours=8),
    },
    {
        "notification_type": "new_event",
        "recipient": marco,
        "channel": "push",
        "title": "New event: Franciacorta Track Day",
        "body": (
            "A new track day has been published at Franciacorta circuit. "
            "Early bird registration is open until next Friday. Limited to 40 riders."
        ),
        "url": "/en/events/",
        "status": "sent",
        "sent_at": now - timedelta(days=1, hours=4),
    },
    {
        "notification_type": "membership_approved",
        "recipient": marco,
        "channel": "email",
        "title": "Your membership has been renewed",
        "body": (
            "Your Premium Membership for 2026 has been confirmed. "
            "Your new card is ready for download in the members area."
        ),
        "url": "/en/members/",
        "status": "sent",
        "sent_at": now - timedelta(days=3),
    },
    {
        "notification_type": "aid_request",
        "recipient": marco,
        "channel": "in_app",
        "title": "New mutual aid request nearby",
        "body": (
            "Roberto Colombo needs roadside assistance near Bergamo. "
            "He has a flat tyre and is 12 km from your location. Can you help?"
        ),
        "url": "/en/mutual-aid/",
        "status": "sent",
        "sent_at": now - timedelta(days=5, hours=6),
    },
]

for n in notifications:
    NotificationQueue.objects.create(**n)

total = NotificationQueue.objects.filter(recipient=marco, status="sent").count()
print(f"Created {len(notifications)} notifications for {marco.username}")
print(f"Total sent notifications: {total}")
