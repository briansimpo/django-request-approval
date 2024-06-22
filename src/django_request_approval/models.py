
from abc import abstractmethod
import uuid
from datetime import date
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group


class RequestStatus(models.TextChoices):
    PENDING = 'Pending'
    COMPLETED = 'Completed'


class ApprovalStatus(models.TextChoices):
    APPROVED = 'Approved'
    REJECTED = 'Rejected'


class BaseStage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    level = models.IntegerField()
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
    
    @classmethod
    def first_stage(cls):
        stage = cls.objects.get(level=1)
        if not stage:
            raise Exception("Approval Stage Not Found")
        return stage
    
    @classmethod
    def last_stage(cls):
        stage = cls.objects.order_by("-level").first()
        return stage


class BaseApprover(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    request_stage = None
    group = models.ForeignKey(Group, related_name="+", on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.group.name
    
    @classmethod
    def get_by_stage(cls, stage):
        if not isinstance(stage, cls):
            stage = cls.objects.get(id=stage)
        return cls.objects.filter(stage=stage)
    
    @classmethod
    def get_by_group(cls, group):
        if not isinstance(group, cls):
            group = cls.objects.get(id=group)
        return cls.objects.filter(group=group)
    

class BaseRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    request_stage = None
    request_status = models.CharField(max_length=255,choices=RequestStatus.choices, default=RequestStatus.PENDING, blank=True, null=True)
    request_date = models.DateField(auto_now=True, blank=True, null=True)
    request_summary = models.TextField(blank=True, null=True)
    approval_status = models.CharField(max_length=255,choices=ApprovalStatus.choices, default=RequestStatus.PENDING, blank=True, null=True)
    approval_date = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    @abstractmethod
    def get_last_stage(self):
        pass
    
    def is_last_stage(self):
        last_stage = self.get_last_stage()
        return self.request_stage == last_stage

    def approve(self):
        self.approval_status = ApprovalStatus.APPROVED
        self.approval_date = date.today()

    def reject(self):
        self.approval_status = ApprovalStatus.REJECTED
        self.approval_date = date.today()
        
    def complete(self):
        self.request_status = RequestStatus.COMPLETED
    
    def is_pending(self):
        return self.request_status==RequestStatus.PENDING

    def is_completed(self):
        return self.request_status==RequestStatus.COMPLETED

    def is_approved(self):
        return self.approval_status==ApprovalStatus.APPROVED

    def is_rejected(self):
        return self.approval_status==ApprovalStatus.REJECTED
   

class BaseApproval(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    request = None
    request_stage = None
    decision = models.CharField(max_length=255, choices=ApprovalStatus.choices)
    comment = models.CharField(max_length=255, blank=True, null=True)
    approver = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    approval_date = models.DateField(auto_now=True)

    class Meta:
        abstract = True

    def is_approved(self):
        return self.decision==ApprovalStatus.APPROVED

    def is_rejected(self):
        return self.decision==ApprovalStatus.REJECTED
