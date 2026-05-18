from django.db.models import Case, IntegerField, Q, Value, When
from django.utils import timezone

from .models import Grant, Notification, User


def recommended_grants_for(user: User):
    interests = [item.strip().lower() for item in user.interests.split(',') if item.strip()]
    interest_query = Q()
    for item in interests:
        interest_query |= Q(category__name__icontains=item) | Q(title__icontains=item) | Q(description__icontains=item)

    queryset = Grant.objects.filter(deadline__gte=timezone.localdate())
    if user.education_level:
        queryset = queryset.annotate(
            level_score=Case(
                When(education_level__icontains=user.education_level, then=Value(2)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
    else:
        queryset = queryset.annotate(level_score=Value(0, output_field=IntegerField()))

    if interests:
        queryset = queryset.filter(interest_query | Q(education_level__icontains=user.education_level))

    return queryset.order_by('-level_score', 'deadline')[:8]


def create_deadline_notifications(user: User):
    grants = Grant.objects.filter(deadline__gte=timezone.localdate())
    for grant in grants:
        if grant.is_deadline_soon:
            message = f'Скоро дедлайн по программе "{grant.title}" - {grant.deadline:%d.%m.%Y}.'
            Notification.objects.get_or_create(user=user, message=message)


def notify_matching_new_grant(grant: Grant):
    users = User.objects.filter(role=User.Role.STUDENT)
    for user in users:
        text = f'Появилась новая возможность, подходящая вашему профилю: {grant.title}.'
        if grant in list(recommended_grants_for(user)):
            Notification.objects.get_or_create(user=user, message=text)
