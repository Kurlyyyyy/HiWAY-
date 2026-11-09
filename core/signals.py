from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name == 'core':
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@hiway.local', 'group11')
            print("Default admin account created: admin / group11")