from mongoengine import Document, EmbeddedDocument, fields
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
import uuid


class UserProfile(EmbeddedDocument):
    """Embedded user profile document"""

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

    # Basic info
    user_type = fields.StringField(max_length=20, choices=USER_TYPES, default="farmer")
    phone_number = fields.StringField(max_length=17, unique=True, sparse=True)
    alternate_phone = fields.StringField(max_length=17)
    date_of_birth = fields.DateTimeField()
    gender = fields.StringField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
    )

    # Address
    address_line1 = fields.StringField(max_length=255)
    address_line2 = fields.StringField(max_length=255)
    village = fields.StringField(max_length=100)
    district = fields.StringField(max_length=100)
    state = fields.StringField(max_length=100)
    country = fields.StringField(max_length=100, default="India")
    pincode = fields.StringField(max_length=10)
    latitude = fields.FloatField(min_value=-90, max_value=90)
    longitude = fields.FloatField(min_value=-180, max_value=180)

    # Farmer specific
    farm_size = fields.FloatField()
    farming_experience = fields.IntField()
    education_level = fields.StringField(max_length=20, choices=EDUCATION_LEVELS)
    primary_crops = fields.ListField(fields.StringField(max_length=100))
    livestock = fields.DictField()
    farming_type = fields.StringField(
        max_length=20,
        choices=[
            ("organic", "Organic"),
            ("conventional", "Conventional"),
            ("mixed", "Mixed"),
        ],
        default="conventional",
    )

    # Preferences
    language = fields.StringField(max_length=10, default="en")
    notification_enabled = fields.BooleanField(default=True)
    sms_enabled = fields.BooleanField(default=True)
    email_enabled = fields.BooleanField(default=True)
    whatsapp_enabled = fields.BooleanField(default=False)

    # Verification
    phone_verified = fields.BooleanField(default=False)
    email_verified = fields.BooleanField(default=False)
    kyc_verified = fields.BooleanField(default=False)
    kyc_document_type = fields.StringField(max_length=20)
    kyc_document_number = fields.StringField(max_length=50)

    # Metadata
    profile_picture_url = fields.StringField(max_length=500)
    bio = fields.StringField()
    last_login_ip = fields.StringField(max_length=45)
    device_token = fields.StringField(max_length=255)

    # Timestamps
    created_at = fields.DateTimeField(default=datetime.now)
    updated_at = fields.DateTimeField(default=datetime.now)


class MongoUser(Document):
    """MongoDB User document"""

    # Basic user info
    username = fields.StringField(required=True, unique=True, max_length=150)
    email = fields.EmailField(required=True, unique=True)
    first_name = fields.StringField(max_length=150)
    last_name = fields.StringField(max_length=150)
    password = fields.StringField(required=True)  # Will store hashed password

    # Status fields
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)

    # Timestamps
    date_joined = fields.DateTimeField(default=datetime.now)
    last_login = fields.DateTimeField()

    # Embedded profile
    profile = fields.EmbeddedDocumentField(UserProfile)

    meta = {
        "collection": "users",
        "indexes": [
            "username",
            "email",
            "profile.phone_number",
            ("is_active", "date_joined"),
        ],
    }

    def set_password(self, raw_password):
        """Set password with Django's hash method"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check password against hash"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class MongoSubscription(Document):
    """MongoDB Subscription document"""

    PLAN_TYPES = [
        ("free", "Free"),
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("enterprise", "Enterprise"),
    ]

    user_id = fields.ObjectIdField(required=True)  # Reference to MongoUser
    plan_type = fields.StringField(max_length=20, choices=PLAN_TYPES, default="free")
    start_date = fields.DateTimeField(required=True)
    end_date = fields.DateTimeField(required=True)
    is_active = fields.BooleanField(default=True)
    features = fields.DictField()
    price = fields.DecimalField(min_value=0, precision=2)
    payment_id = fields.StringField(max_length=100)
    payment_method = fields.StringField(max_length=50)
    auto_renew = fields.BooleanField(default=False)

    created_at = fields.DateTimeField(default=datetime.now)
    updated_at = fields.DateTimeField(default=datetime.now)

    meta = {
        "collection": "subscriptions",
        "indexes": ["user_id", ("user_id", "is_active"), "end_date"],
    }


class MongoActivityLog(Document):
    """MongoDB Activity Log document"""

    user_id = fields.ObjectIdField(required=True)
    activity_type = fields.StringField(max_length=50, required=True)
    description = fields.StringField(required=True)
    ip_address = fields.StringField(max_length=45)
    user_agent = fields.StringField(max_length=255)
    metadata = fields.DictField()

    created_at = fields.DateTimeField(default=datetime.now)

    meta = {
        "collection": "activity_logs",
        "indexes": [
            "user_id",
            ("user_id", "-created_at"),
            "activity_type",
            "-created_at",
        ],
    }


class MongoNotification(Document):
    """MongoDB Notification document"""

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

    user_id = fields.ObjectIdField(required=True)
    notification_type = fields.StringField(max_length=20, choices=NOTIFICATION_TYPES)
    channel = fields.StringField(max_length=20, choices=CHANNELS, default="in_app")
    title = fields.StringField(max_length=200, required=True)
    message = fields.StringField(required=True)
    data = fields.DictField()
    is_read = fields.BooleanField(default=False)
    read_at = fields.DateTimeField()
    is_sent = fields.BooleanField(default=False)
    sent_at = fields.DateTimeField()
    priority = fields.IntField(default=5, min_value=1, max_value=10)
    expires_at = fields.DateTimeField()

    created_at = fields.DateTimeField(default=datetime.now)

    meta = {
        "collection": "notifications",
        "indexes": [
            "user_id",
            ("user_id", "is_read"),
            ("user_id", "-created_at"),
            "expires_at",
        ],
    }


class MongoFeedback(Document):
    """MongoDB Feedback document"""

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

    ticket_id = fields.UUIDField(default=uuid.uuid4, unique=True)
    user_id = fields.ObjectIdField(required=True)
    feedback_type = fields.StringField(max_length=20, choices=FEEDBACK_TYPES)
    subject = fields.StringField(max_length=200, required=True)
    description = fields.StringField(required=True)
    attachments = fields.ListField(fields.StringField())
    status = fields.StringField(max_length=20, choices=STATUS_CHOICES, default="open")
    priority = fields.IntField(default=5, min_value=1, max_value=10)
    assigned_to_id = fields.ObjectIdField()
    resolution = fields.StringField()
    resolved_at = fields.DateTimeField()
    rating = fields.IntField(min_value=1, max_value=5)

    created_at = fields.DateTimeField(default=datetime.now)
    updated_at = fields.DateTimeField(default=datetime.now)

    meta = {
        "collection": "feedbacks",
        "indexes": ["user_id", "ticket_id", ("user_id", "status"), "status"],
    }


class MongoApiKey(Document):
    """MongoDB API Key document"""

    user_id = fields.ObjectIdField(required=True)
    name = fields.StringField(max_length=100, required=True)
    key = fields.StringField(max_length=64, required=True, unique=True)
    secret = fields.StringField(max_length=64, required=True)
    is_active = fields.BooleanField(default=True)
    permissions = fields.ListField(fields.StringField())
    rate_limit = fields.IntField(default=1000)
    last_used = fields.DateTimeField()
    expires_at = fields.DateTimeField()

    created_at = fields.DateTimeField(default=datetime.now)
    updated_at = fields.DateTimeField(default=datetime.now)

    meta = {
        "collection": "api_keys",
        "indexes": ["user_id", "key", ("user_id", "is_active")],
    }
