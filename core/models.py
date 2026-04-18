from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ==============================
# PROFILE (USER ROLES)
# ==============================

class Profile(models.Model):
    ROLE_CHOICES = [
        ('reception', 'Receptionist'),
        ('upload1', 'Upload Staff 1'),
        ('upload2', 'Upload Staff 2'),
        ('submission', 'Submission'),
        ('tax', 'Tax/VAT'),
        ('finance', 'Finance'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# ==============================
# CASE MODEL
# ==============================

class Case(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
    ]

    customer_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    product_type = models.CharField(max_length=255)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')

    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.customer_name} - {self.product_type}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Create first task automatically
        if is_new:
            first_user = get_user_by_role('reception')

            Task.objects.create(
                case=self,
                task_type='cv',
                assigned_to=first_user
            )


# ==============================
# TASK MODEL
# ==============================

class Task(models.Model):

    TASK_TYPES = [
        ('cv', 'CV Preparation'),
        ('upload_a', 'Upload Website A'),
        ('upload_b', 'Upload Website B'),
        ('submission', 'Submission'),
        ('tax', 'Tax/VAT'),
        ('payment', 'Payment'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='tasks')
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.task_type} - {self.case}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # When task is completed → trigger next
        if not is_new and self.status == 'done' and self.completed_at is None:
            self.completed_at = timezone.now()
            super().save(update_fields=['completed_at'])

            create_next_task(self)


# ==============================
# DOCUMENT MODEL
# ==============================

class Document(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.case}"


# ==============================
# PAYMENT MODEL
# ==============================

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.amount} - {self.case}"


# ==============================
# HELPER FUNCTIONS
# ==============================

def get_user_by_role(role_name):
    try:
        profile = Profile.objects.get(role=role_name)
        return profile.user
    except Profile.DoesNotExist:
        return None


def create_next_task(task):
    flow = [
        ('cv', 'reception'),
        ('upload_a', 'upload1'),
        ('upload_b', 'upload2'),
        ('submission', 'submission'),
        ('tax', 'tax'),
        ('payment', 'finance'),
    ]

    try:
        current_index = [f[0] for f in flow].index(task.task_type)
        next_task_type, next_role = flow[current_index + 1]
    except (ValueError, IndexError):
        task.case.status = 'completed'
        task.case.save()
        return

    next_user = get_user_by_role(next_role)

    Task.objects.create(
        case=task.case,
        task_type=next_task_type,
        assigned_to=next_user
    )