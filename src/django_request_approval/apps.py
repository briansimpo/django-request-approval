from django.apps import AppConfig


class DjangoApproval(AppConfig):
    name = 'django_approval'
    label = 'approval'


APP_NAME = DjangoApproval.label
