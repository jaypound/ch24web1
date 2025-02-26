# notifications.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_ticket_notification(ticket):
    """
    Send email notification when a new support ticket is created.
    
    Args:
        ticket: SupportTicket instance that was just created
    """
    # Email subject
    subject = f'New Support Ticket #{ticket.ticket_no}: {ticket.subject}'
    
    # Build context for email template
    context = {
        'ticket': ticket,
        'category': dict(ticket.TICKET_CATEGORIES).get(ticket.category, ''),
        'urgency': dict(ticket.URGENCY_CHOICES).get(ticket.urgency, ''),
        'created_by': ticket.created_by.get_full_name() if ticket.created_by else 'Anonymous',
        'creator_info': ticket.creator.first_name + " " + ticket.creator.last_name if ticket.creator else 'N/A',
        'program': ticket.program.title if ticket.program else 'N/A',
        'episode': ticket.episode.title if ticket.episode else 'N/A'
    }
    
    # Render email content from template
    html_content = render_to_string('support/email/ticket_notification.html', context)
    text_content = render_to_string('support/email/ticket_notification.txt', context)
    
    # Get admin email addresses from settings
    admin_emails = getattr(settings, 'SUPPORT_NOTIFICATION_EMAILS', [])
    if not admin_emails:
        # Fallback to ADMINS setting if SUPPORT_NOTIFICATION_EMAILS is not set
        admin_emails = [email for name, email in settings.ADMINS]
    
    # Send email
    send_mail(
        subject=subject,
        message=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=admin_emails,
        html_message=html_content,
        fail_silently=False
    )
