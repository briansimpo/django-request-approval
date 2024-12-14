
from abc import abstractmethod
from datetime import date
from django.db import IntegrityError, models
from django.conf import settings
from django.contrib.auth.models import Group
from django.forms import ValidationError
from django.http import Http404
from model_utils.models import TimeStampedModel, UUIDModel


class RequestStatus(models.TextChoices):
    PENDING = 'Pending'
    COMPLETED = 'Completed'


class ApprovalStatus(models.TextChoices):
    APPROVED = 'Approved'
    REJECTED = 'Rejected'


class BaseStage(UUIDModel, TimeStampedModel):
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
            raise Http404("Approval stage is not found or configured")
        return stage
    
    @classmethod
    def last_stage(cls):
        if cls.objects.count() == 1:
            return cls.objects.first()
        else:
            stage = cls.objects.order_by("-level").first()
            return stage


class BaseApprover(UUIDModel, TimeStampedModel):
    request_stage = None
    group = models.ForeignKey(Group, related_name="+", on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.group.name
    
    
    def exists(self):
        return self.__class__.objects.filter(group=self.group).exists()
    
    def _validation_message(self):
        return "You cannot have the same group of users approving requests at multiple stages."
    
    def validate(self):
        if self.exists():
            raise IntegrityError(self._validation_message())

    def clean(self):
        if self.exists():
            raise ValidationError({
                "group": self._validation_message()
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
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
    

class BaseRequest(UUIDModel, TimeStampedModel):
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
   

class BaseApproval(UUIDModel, TimeStampedModel):
    request = None
    request_stage = None
    decision = models.CharField(max_length=255, choices=ApprovalStatus.choices)
    comment = models.CharField(max_length=255, blank=True, null=True)
    approver = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.DO_NOTHING)
    approval_date = models.DateField(auto_now=True)

    class Meta:
        abstract = True

    def is_approved(self):
        return self.decision==ApprovalStatus.APPROVED

    def is_rejected(self):
        return self.decision==ApprovalStatus.REJECTED
