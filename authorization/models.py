from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

User = get_user_model()


class AuthorizedQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_trashed=False)

    def trashed(self):
        return self.filter(is_trashed=True)

    def for_user(self, user, action='view'):
        if user is None or not user.is_authenticated:
            return self.none()

        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name

        if user.has_perm(f'{app_label}.{action}_all_{model_name}'):
            return self

        if user.has_perm(f'{app_label}.{action}_own_{model_name}'):
            return self.filter(created_by=user)

        return self.none()


class AuthorizedManager(models.Manager):
    def get_queryset(self):
        return AuthorizedQuerySet(self.model, using=self._db).active()

    def with_trashed(self):
        return AuthorizedQuerySet(self.model, using=self._db)

    def trashed(self):
        return self.with_trashed().trashed()

    def for_user(self, user, action='view'):
        return self.get_queryset().for_user(user, action)


class AuthorizationAuditModel(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    is_trashed = models.BooleanField(default=False)
    trashed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    trashed_at = models.DateTimeField(null=True, blank=True)
    restored_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    restored_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    deleted_at = models.DateTimeField(null=True, blank=True)
    force_deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    force_deleted_at = models.DateTimeField(null=True, blank=True)

    objects = AuthorizedManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        permissions = [
            ('view_all_records', 'Can view all records'),
            ('view_own_records', 'Can view own records'),
            ('view_single_records', 'Can view single records'),
            ('edit_all_records', 'Can edit all records'),
            ('edit_own_records', 'Can edit own records'),
            ('create_records', 'Can create records'),
            ('trash_all_records', 'Can trash all records'),
            ('trash_own_records', 'Can trash own records'),
            ('restore_all_records', 'Can restore all records'),
            ('restore_own_records', 'Can restore own records'),
            ('force_delete_all_records', 'Can force delete all records'),
            ('force_delete_own_records', 'Can force delete own records'),
        ]

    def set_created_user(self, user):
        if user and user.is_authenticated and not self.created_by_id:
            self.created_by = user

    def set_updated_user(self, user):
        if user and user.is_authenticated:
            self.updated_by = user

    def trash(self, user=None):
        self.is_trashed = True
        self.trashed_by = user if user and user.is_authenticated else None
        self.trashed_at = timezone.now()
        self.deleted_by = self.trashed_by
        self.deleted_at = self.trashed_at
        self.save(update_fields=['is_trashed', 'trashed_by', 'trashed_at', 'deleted_by', 'deleted_at', 'updated_at'])
        AuthorizationActivityLog.log(self, 'trash', user)

    def restore(self, user=None):
        self.is_trashed = False
        self.restored_by = user if user and user.is_authenticated else None
        self.restored_at = timezone.now()
        self.save(update_fields=['is_trashed', 'restored_by', 'restored_at', 'updated_at'])
        AuthorizationActivityLog.log(self, 'restore', user)

    def force_delete(self, user=None, using=None, keep_parents=False):
        self.force_deleted_by = user if user and user.is_authenticated else None
        self.force_deleted_at = timezone.now()
        AuthorizationActivityLog.log(self, 'force_delete', user)
        return super().delete(using=using, keep_parents=keep_parents)

    def delete(self, using=None, keep_parents=False, user=None):
        self.trash(user=user)


class PermissionLabel(models.Model):
    ACTION_CHOICES = (
        ('view_all', 'View all'),
        ('view_single', 'View single'),
        ('edit', 'Edit'),
        ('create', 'Create'),
        ('delete', 'Delete'),
        ('trash', 'Trash'),
        ('restore', 'Restore'),
        ('force_delete', 'Force delete'),
    )

    SCOPE_CHOICES = (
        ('all', 'All / full access'),
        ('own', 'Own / personal access'),
        ('single', 'Single record access'),
    )

    app_label = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    scope = models.CharField(max_length=50, choices=SCOPE_CHOICES, default='all')
    codename = models.CharField(max_length=150, unique=True)

    label_en = models.CharField(max_length=200)
    label_dari = models.CharField(max_length=200, blank=True)
    label_pashto = models.CharField(max_length=200, blank=True)
    label_arabic = models.CharField(max_length=200, blank=True)

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['app_label', 'model_name', 'action', 'scope']
        unique_together = ('app_label', 'model_name', 'action', 'scope')

    def __str__(self):
        return f'{self.app_label}.{self.model_name}: {self.label_en}'


class AuthorizationActivityLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('trash', 'Trash'),
        ('restore', 'Restore'),
        ('delete', 'Delete'),
        ('force_delete', 'Force delete'),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=255, blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='authorization_activity_logs')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} - {self.object_repr}'

    @classmethod
    def log(cls, instance, action, user=None):
        return cls.objects.create(
            content_type=ContentType.objects.get_for_model(instance.__class__),
            object_id=instance.pk,
            object_repr=str(instance),
            action=action,
            user=user if user and user.is_authenticated else None,
        )
