
# Django Request Approval

This is a package of base classes for approval process. 
To use this package, you have to create classes that inherit base classes from this package.
Detailed documentation is in the "docs" directory.

## Quick start

1. Add `django_request_approval` to your INSTALLED_APPS setting like this::

```python 

    INSTALLED_APPS = [
        ...,
        "django_request_approval",
    ]

```

## Usage


### List of Base classes

The package contains 4 base classes
1. BaseStage -> Represents Approval Stages (Stage 1, Stage 2, Stage 3)
2. BaseApprover -> Represents Stage Approver (Stage, User Group)
3. BaseRequest -> Represents the Request to be approved
4. BaseApproval -> Represents the actual Approval made by Approver


