

from abc import ABC, abstractmethod
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import ApprovalStatus, BaseApproval, BaseApprover, BaseRequest, BaseStage, RequestStatus


class ApproverService(ABC):
    approver_model: BaseApprover = None
    request_model: BaseRequest = None
    approval_model: BaseApproval = None
  
    def __init__(self, approver: User) -> None:
        self.approver = approver

    def get_approver(self) -> BaseApprover:
        user_group = self.approver.groups.all()
        return self.approver_model.objects.filter(group__in=user_group).first()
    
    def get_requests(self):
        approver = self.get_approver()
        if not approver:
            raise PermissionDenied
        
        return self.request_model.objects.filter(
            request_status=RequestStatus.PENDING,
            approval_status=RequestStatus.PENDING,
            request_stage=approver.request_stage
        )
    
    def get_history(self):
        approver = self.get_approver()
        if not approver:
            raise PermissionDenied
        
        return self.approval_model.objects.filter(request_stage=approver.request_stage)

    
class ApprovalService(ABC):
    approver_model: BaseApprover = None
    request_model: BaseRequest = None
    approval_model: BaseApproval = None
    stage_model: BaseStage = None

    def __init__(self, approver: User, request: BaseRequest, decision: str, comment: str):
        self.approver = approver
        self.request = request
        self.decision = decision
        self.comment = comment
    
    def get_decision(self):
        if str(self.decision).lower() == (ApprovalStatus.APPROVED).lower():
            return ApprovalStatus.APPROVED
        if str(self.decision).lower() == (ApprovalStatus.REJECTED).lower():
            return ApprovalStatus.REJECTED
        
    def create_approval(self):
        approval = self.approval_model.objects.create(
            request=self.request,
            request_stage=self.request.request_stage,
            approver=self.approver,
            comment=self.comment,
            decision=self.get_decision()
        )
        return approval

    def get_next_stage(self):
        current_level = self.request.request_stage.level
        return self.stage_model.objects.filter(level__gt=current_level).first()

    def approve_request(self):
        if self.request.is_last_stage():
            self.request.approve()
            self.request.complete()
            self.request.save()
            self.post_request_approve()
        else:
            next_stage = self.get_next_stage()
            self.request.request_date = next_stage
            self.request.save()

    def reject_request(self):
        request = self.request
        request.reject()
        request.complete()
        request.save()
        self.post_request_reject()

    def process(self):
        approval = self.create_approval()
        if approval.is_approved():
            self.approve_request()
        elif approval.is_rejected():
            self.reject_request()
        return approval
    

    @abstractmethod
    def post_request_approve(self):
       pass
    
    @abstractmethod
    def post_request_reject(self):
       pass


        


