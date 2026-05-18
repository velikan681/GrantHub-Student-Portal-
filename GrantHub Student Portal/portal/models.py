from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Студент'
        ADMIN = 'admin', 'Администратор'
        ORGANIZATION = 'organization', 'Представитель организации'

    username = None
    full_name = models.CharField('ФИО', max_length=180)
    email = models.EmailField('Email', unique=True)
    role = models.CharField('Роль', max_length=20, choices=Role.choices, default=Role.STUDENT)
    university = models.CharField('Университет', max_length=180, blank=True)
    faculty = models.CharField('Факультет', max_length=180, blank=True)
    course = models.PositiveSmallIntegerField('Курс', null=True, blank=True)
    education_level = models.CharField('Уровень образования', max_length=80, blank=True)
    interests = models.CharField('Интересы', max_length=255, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    objects = UserManager()

    def __str__(self):
        return self.full_name or self.email


class Category(models.Model):
    name = models.CharField('Название', max_length=120, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Grant(models.Model):
    class OpportunityType(models.TextChoices):
        GRANT = 'grant', 'Грант'
        SCHOLARSHIP = 'scholarship', 'Стипендия'
        CONTEST = 'contest', 'Конкурс'
        INTERNSHIP = 'internship', 'Стажировка'
        EXCHANGE = 'exchange', 'Обменная программа'

    title = models.CharField('Название', max_length=220)
    description = models.TextField('Описание')
    organization = models.CharField('Организатор', max_length=180)
    country = models.CharField('Страна', max_length=100)
    category = models.ForeignKey(Category, verbose_name='Направление', on_delete=models.PROTECT)
    opportunity_type = models.CharField('Тип возможности', max_length=20, choices=OpportunityType.choices)
    education_level = models.CharField('Уровень образования', max_length=80)
    requirements = models.TextField('Требования')
    documents = models.TextField('Документы')
    deadline = models.DateField('Дедлайн')
    official_link = models.URLField('Официальная ссылка')
    created_by = models.ForeignKey(User, verbose_name='Автор', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Грантовая возможность'
        verbose_name_plural = 'Грантовые возможности'
        ordering = ['deadline', 'title']

    @property
    def is_deadline_soon(self):
        delta = self.deadline - timezone.localdate()
        return 0 <= delta.days <= 14

    def __str__(self):
        return self.title


class Application(models.Model):
    class Status(models.TextChoices):
        REVIEW = 'review', 'На рассмотрении'
        APPROVED = 'approved', 'Одобрено'
        REJECTED = 'rejected', 'Отклонено'

    user = models.ForeignKey(User, verbose_name='Студент', on_delete=models.CASCADE, related_name='applications')
    grant = models.ForeignKey(Grant, verbose_name='Грант', on_delete=models.CASCADE, related_name='applications')
    cv_file = models.FileField('CV', upload_to='applications/cv/', blank=True)
    motivation_letter = models.FileField('Мотивационное письмо', upload_to='applications/motivation/', blank=True)
    certificate_file = models.FileField('Сертификаты', upload_to='applications/certificates/', blank=True)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.REVIEW)
    submitted_at = models.DateTimeField('Дата подачи', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        unique_together = ('user', 'grant')
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.user} - {self.grant}'


class SavedGrant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_grants')
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Сохраненный грант'
        verbose_name_plural = 'Сохраненные гранты'
        unique_together = ('user', 'grant')

    def __str__(self):
        return f'{self.user} сохранил {self.grant}'


class Notification(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField('Сообщение', max_length=255)
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return self.message
