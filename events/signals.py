from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from events.models import RSVP

@receiver(post_save, sender=User)
def send_activation_email(sender, created, instance, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        activation_url = f'{settings.ACTIVATION_URL}/user-activate/{instance.id}/{token}'

        subject = 'Activate your account'
        message = f'Hi {instance.username},\n\nPlease activate your account by clicking the link below:\n{activation_url}\n\nThank you'
        recipient = [instance.email]
        try:
            send_mail( subject, message, settings.EMAIL_HOST_USER, recipient, fail_silently=False)
        except Exception as e:
            print(f'Failed to send email to {instance.email}: {str(e)}')

@receiver(post_save, sender=User)
def assign_role(sender, instance, created, **kwargs):
    if created:
        user_group, created = Group.objects.get_or_create(name='Participant')
        instance.groups.add(user_group)
        instance.save()


@receiver(post_save, sender=RSVP)
def send_rsvp_signal(sender, instance, created, **kwargs):
    if created:
        user= instance.user
        event = instance.event
        token = default_token_generator.make_token(user)
        activation_url = f'{settings.ACTIVATION_URL}/activate-rsvp/{instance.id}/{token}/'
        subject = f'Your presence is requested for {event.name}'
        message = f'Hi {user.username}\n\nWe are delighted to invite you to our {event.name}.\nThe event will be held on {event.start_date} to {event.end_date}\n\nWe kindly request you that you confirm your attendance by clicking the clicking the link below:\n{activation_url}\n\nThank you.'
        recipient = [user.email]
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient, fail_silently=False)
        except Exception as e:
            print(f'Failed to send mail to {user.email}:', str(e))
    
