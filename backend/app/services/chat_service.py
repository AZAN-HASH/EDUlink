from ..extensions import db, socketio
from ..models import Club, ClubMembership, ClubMessage, DirectMessage, DirectMessageThread, User
from .notification_service import create_notification


def get_or_create_thread(user_one_id, user_two_id):
    first, second = sorted([user_one_id, user_two_id])
    thread = DirectMessageThread.query.filter_by(
        participant_one_id=first, participant_two_id=second
    ).first()
    if thread:
        return thread

    thread = DirectMessageThread(participant_one_id=first, participant_two_id=second)
    db.session.add(thread)
    db.session.commit()
    return thread


def send_direct_message(sender_id, recipient_id, body):
    sender = db.session.get(User, sender_id)
    recipient = db.session.get(User, recipient_id)
    if not sender or not recipient:
        raise ValueError("Sender or recipient not found.")

    thread = get_or_create_thread(sender_id, recipient_id)
    message = DirectMessage(thread_id=thread.id, sender_id=sender_id, recipient_id=recipient_id, body=body.strip())
    db.session.add(message)
    db.session.commit()

    payload = message.to_dict()
    socketio.emit("direct_message", payload, room=f"user_{recipient_id}")
    socketio.emit("direct_message", payload, room=f"user_{sender_id}")
    create_notification(
        recipient_id,
        sender_id,
        "message",
        f"{sender.username} sent you a message.",
        entity_type="thread",
        entity_id=thread.id,
    )
    return message


def send_club_message(sender_id, club_id, body):
    membership = ClubMembership.query.filter_by(user_id=sender_id, club_id=club_id, status="approved").first()
    club = db.session.get(Club, club_id)
    if not membership or not club:
        raise ValueError("Only approved club members can send club messages.")

    message = ClubMessage(club_id=club_id, sender_id=sender_id, body=body.strip())
    db.session.add(message)
    db.session.commit()

    payload = message.to_dict()
    socketio.emit("club_message", payload, room=f"club_{club_id}")

    members = ClubMembership.query.filter_by(club_id=club_id, status="approved").all()
    for member in members:
        if member.user_id != sender_id:
            create_notification(
                member.user_id,
                sender_id,
                "club_message",
                f"New club message in {club.name}.",
                entity_type="club",
                entity_id=club_id,
            )
    return message
