from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import uuid

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)


class UserProfile(models.Model):
    """Extended user profile for farmers"""

    USER_TYPES = [
        ("farmer", "Farmer"),
        ("trader", "Trader"),
        ("expert", "Agricultural Expert"),
        ("admin", "Administrator"),
    ]

    EDUCATION_LEVELS = [
        ("primary", "Primary School"),
        ("secondary", "Secondary School"),
        ("higher_secondary", "Higher Secondary"),
        ("graduate", "Graduate"),
        ("post_graduate", "Post Graduate"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default="farmer")
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, unique=True
    )
    alternate_phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        blank=True,
    )

    # Address
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    village = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="India")
    pincode = models.CharField(max_length=10)
    latitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    # Farmer specific
    farm_size = models.FloatField(
        null=True, blank=True, help_text="Total farm size in hectares"
    )
    farming_experience = models.IntegerField(
        null=True, blank=True, help_text="Years of farming experience"
    )
    education_level = models.CharField(
        max_length=20, choices=EDUCATION_LEVELS, blank=True
    )
    primary_crops = models.JSONField(
        default=list, blank=True, help_text="List of primary crops grown"
    )
    livestock = models.JSONField(
        default=dict, blank=True, help_text="Livestock details"
    )
    farming_type = models.CharField(
        max_length=20,
        choices=[
            ("organic", "Organic"),
            ("conventional", "Conventional"),
            ("mixed", "Mixed"),
        ],
        default="conventional",
    )

    # Preferences
    language = models.CharField(max_length=10, default="en")
    notification_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    whatsapp_enabled = models.BooleanField(default=False)

    # Verification
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    kyc_verified = models.BooleanField(default=False)
    kyc_document_type = models.CharField(max_length=20, blank=True)
    kyc_document_number = models.CharField(max_length=50, blank=True)

    # Metadata
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    device_token = models.CharField(
        max_length=255, blank=True, help_text="FCM token for push notifications"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "user_type"]),
            models.Index(fields=["phone_number"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

    @property
    def full_address(self):
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.extend([self.village, self.district, self.state, self.pincode])
        return ", ".join(filter(None, parts))


class Subscription(models.Model):
    """User subscription plans"""

    PLAN_TYPES = [
        ("free", "Free"),
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("enterprise", "Enterprise"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default="free")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    features = models.JSONField(default=dict, help_text="Plan features and limits")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["end_date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_type_display()}"


class ActivityLog(models.Model):
    """User activity tracking"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="activity_logs"
    )
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["activity_type"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.created_at}"


class Notification(models.Model):
    """User notifications"""

    NOTIFICATION_TYPES = [
        ("info", "Information"),
        ("warning", "Warning"),
        ("alert", "Alert"),
        ("success", "Success"),
        ("error", "Error"),
    ]

    CHANNELS = [
        ("in_app", "In-App"),
        ("email", "Email"),
        ("sms", "SMS"),
        ("push", "Push Notification"),
        ("whatsapp", "WhatsApp"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=20, choices=CHANNELS, default="in_app")
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Feedback(models.Model):
    """User feedback and support"""

    FEEDBACK_TYPES = [
        ("bug", "Bug Report"),
        ("feature", "Feature Request"),
        ("complaint", "Complaint"),
        ("suggestion", "Suggestion"),
        ("appreciation", "Appreciation"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedbacks")
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    attachments = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    priority = models.IntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_feedbacks",
    )
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["ticket_id"]),
        ]

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"


class ApiKey(models.Model):
    """API keys for external integrations"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    secret = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    permissions = models.JSONField(
        default=list, help_text="List of permitted endpoints"
    )
    rate_limit = models.IntegerField(default=1000, help_text="Requests per hour")
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["key"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name}"
