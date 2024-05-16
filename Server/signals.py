from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db import connection


@receiver(post_migrate, sender=AppConfig)
def reset_database(sender, **kwargs):
    with connection.cursor() as cursor:
        cursor.execute('DROP DATABASE IF EXISTS server')
        cursor.execute('CREATE DATABASE server')
