from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from portal.models import Application, Category, Grant, Notification, SavedGrant, User


class Command(BaseCommand):
    help = 'Создает расширенные демонстрационные данные для GrantHub Student Portal.'

    def handle(self, *args, **options):
        today = timezone.localdate()

        categories = self.create_categories()
        users = self.create_users()
        grants = self.create_grants(categories, users, today)
        self.create_student_activity(users, grants)

        self.stdout.write(self.style.SUCCESS('Расширенные демонстрационные данные созданы.'))
        self.stdout.write(f'Категорий: {Category.objects.count()}')
        self.stdout.write(f'Пользователей: {User.objects.count()}')
        self.stdout.write(f'Грантов: {Grant.objects.count()}')
        self.stdout.write(f'Заявок: {Application.objects.count()}')
        self.stdout.write(f'Сохраненных грантов: {SavedGrant.objects.count()}')
        self.stdout.write('admin@granthub.local / admin12345')
        self.stdout.write('partner@granthub.local / partner12345')
        self.stdout.write('student@granthub.local / student12345')

    def create_categories(self):
        names = [
            'IT',
            'Медицина',
            'Экология',
            'Инженерия',
            'Экономика',
            'Социальные науки',
            'Искусство',
            'Педагогика',
            'Иностранные языки',
            'Право',
            'Журналистика',
            'Биотехнологии',
            'Математика',
            'Архитектура',
            'Агронаука',
            'Государственное управление',
        ]
        return {name: Category.objects.get_or_create(name=name)[0] for name in names}

    def create_users(self):
        users = {}
        base_users = [
            {
                'email': 'admin@granthub.local',
                'password': 'admin12345',
                'full_name': 'Администратор GrantHub',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'email': 'partner@granthub.local',
                'password': 'partner12345',
                'full_name': 'Международный офис университета',
                'role': User.Role.ORGANIZATION,
            },
            {
                'email': 'globalfund@granthub.local',
                'password': 'partner12345',
                'full_name': 'Global Education Fund',
                'role': User.Role.ORGANIZATION,
            },
            {
                'email': 'techlab@granthub.local',
                'password': 'partner12345',
                'full_name': 'TechLab Innovation Center',
                'role': User.Role.ORGANIZATION,
            },
            {
                'email': 'student@granthub.local',
                'password': 'student12345',
                'full_name': 'Алина Каримова',
                'role': User.Role.STUDENT,
                'university': 'Национальный университет',
                'faculty': 'Компьютерные науки',
                'course': 3,
                'education_level': 'Бакалавриат',
                'interests': 'IT, стартапы, инженерия',
            },
            {
                'email': 'timur.student@granthub.local',
                'password': 'student12345',
                'full_name': 'Тимур Юсупов',
                'role': User.Role.STUDENT,
                'university': 'Технический университет',
                'faculty': 'Инженерия',
                'course': 4,
                'education_level': 'Бакалавриат',
                'interests': 'инженерия, робототехника, энергетика',
            },
            {
                'email': 'madina.student@granthub.local',
                'password': 'student12345',
                'full_name': 'Мадина Саидова',
                'role': User.Role.STUDENT,
                'university': 'Медицинская академия',
                'faculty': 'Лечебное дело',
                'course': 5,
                'education_level': 'Магистратура',
                'interests': 'медицина, исследования, биотехнологии',
            },
            {
                'email': 'aziz.student@granthub.local',
                'password': 'student12345',
                'full_name': 'Азиз Рахимов',
                'role': User.Role.STUDENT,
                'university': 'Экономический университет',
                'faculty': 'Финансы',
                'course': 2,
                'education_level': 'Бакалавриат',
                'interests': 'экономика, предпринимательство, аналитика',
            },
        ]

        for data in base_users:
            password = data.pop('password')
            email = data['email']
            user, _ = User.objects.get_or_create(email=email, defaults=data)
            for field, value in data.items():
                setattr(user, field, value)
            user.set_password(password)
            user.save()
            users[email] = user

        return users

    def create_grants(self, categories, users, today):
        partner = users['partner@granthub.local']
        global_fund = users['globalfund@granthub.local']
        tech_lab = users['techlab@granthub.local']

        demo_grants = [
            ('Global Tech Scholarship 2026', 'Стипендия для студентов IT-направлений с оплатой обучения, менторством и карьерной поддержкой.', 'Global Education Fund', 'Германия', 'IT', Grant.OpportunityType.SCHOLARSHIP, 'Бакалавриат', 25, global_fund),
            ('Eco Leaders Grant', 'Грант на исследовательские проекты в области устойчивого развития, климата и городской экологии.', 'Green Future Foundation', 'Нидерланды', 'Экология', Grant.OpportunityType.GRANT, 'Магистратура', 12, global_fund),
            ('Startup Internship Europe', 'Летняя стажировка в технологических стартапах Европы для студентов 2-4 курсов.', 'EU Startup Network', 'Франция', 'IT', Grant.OpportunityType.INTERNSHIP, 'Бакалавриат', 38, tech_lab),
            ('Young Engineers Challenge', 'Международный конкурс инженерных решений для городской инфраструктуры и транспорта.', 'Engineering Alliance', 'Япония', 'Инженерия', Grant.OpportunityType.CONTEST, 'Бакалавриат, Магистратура', 18, partner),
            ('Medical Research Mobility', 'Обменная программа для студентов медицинских вузов с практикой в клиниках-партнерах.', 'Health Academic Network', 'Турция', 'Медицина', Grant.OpportunityType.EXCHANGE, 'Магистратура', 45, global_fund),
            ('Creative Arts Fellowship', 'Стипендия для молодых авторов, дизайнеров и исследователей культуры.', 'Open Culture Institute', 'Италия', 'Искусство', Grant.OpportunityType.SCHOLARSHIP, 'Бакалавриат', 9, partner),
            ('Economics for Development', 'Грант на аналитические проекты по экономическому развитию регионов.', 'Development Lab', 'США', 'Экономика', Grant.OpportunityType.GRANT, 'Магистратура', 30, global_fund),
            ('Women in STEM Award', 'Стипендия для студенток технических и естественно-научных направлений.', 'STEM Equality Fund', 'Канада', 'Инженерия', Grant.OpportunityType.SCHOLARSHIP, 'Бакалавриат', 21, global_fund),
            ('Data Science Bootcamp Grant', 'Финансирование интенсивной программы по анализу данных, Python и машинному обучению.', 'TechLab Innovation Center', 'Сингапур', 'IT', Grant.OpportunityType.GRANT, 'Бакалавриат, Магистратура', 14, tech_lab),
            ('Future Teachers Program', 'Образовательная программа для будущих преподавателей с практикой в школах-партнерах.', 'Education Forward', 'Финляндия', 'Педагогика', Grant.OpportunityType.EXCHANGE, 'Бакалавриат', 33, partner),
            ('Language Excellence Scholarship', 'Стипендия для студентов, изучающих иностранные языки, перевод и межкультурные коммуникации.', 'Linguist Bridge', 'Испания', 'Иностранные языки', Grant.OpportunityType.SCHOLARSHIP, 'Бакалавриат', 27, partner),
            ('Public Policy Fellowship', 'Стажировка в аналитических центрах для студентов государственного управления и права.', 'Policy Lab', 'Великобритания', 'Государственное управление', Grant.OpportunityType.INTERNSHIP, 'Магистратура', 41, global_fund),
            ('Biotech Research Grant', 'Грант на лабораторные исследования в области биотехнологий и молекулярной биологии.', 'BioFuture Institute', 'Швейцария', 'Биотехнологии', Grant.OpportunityType.GRANT, 'Магистратура', 17, global_fund),
            ('Media Innovation Contest', 'Конкурс цифровых медиа-проектов, подкастов и студенческих редакций.', 'Digital Media Hub', 'Польша', 'Журналистика', Grant.OpportunityType.CONTEST, 'Бакалавриат', 11, tech_lab),
            ('Urban Architecture Studio', 'Обменная студия для студентов архитектуры и городского планирования.', 'Urban Lab Europe', 'Дания', 'Архитектура', Grant.OpportunityType.EXCHANGE, 'Бакалавриат, Магистратура', 52, partner),
            ('AgroTech Student Grant', 'Грант на проекты в области умного сельского хозяйства, дронов и мониторинга почв.', 'Agro Innovation Fund', 'Нидерланды', 'Агронаука', Grant.OpportunityType.GRANT, 'Бакалавриат', 24, tech_lab),
            ('Math Olympiad Research Camp', 'Летний исследовательский лагерь для студентов математики и прикладной статистики.', 'Math Science Society', 'Венгрия', 'Математика', Grant.OpportunityType.CONTEST, 'Бакалавриат', 8, partner),
            ('Legal Clinics Exchange', 'Обменная программа для студентов права с участием в юридических клиниках.', 'Justice Education Network', 'Чехия', 'Право', Grant.OpportunityType.EXCHANGE, 'Бакалавриат', 36, global_fund),
            ('Social Impact Grant', 'Грант на студенческие проекты в сфере инклюзии, волонтерства и развития сообществ.', 'Impact Foundation', 'Швеция', 'Социальные науки', Grant.OpportunityType.GRANT, 'Бакалавриат, Магистратура', 16, partner),
            ('FinTech Internship Asia', 'Стажировка в финтех-компаниях с задачами по продуктовой аналитике и платежным системам.', 'Asia FinTech Network', 'Южная Корея', 'Экономика', Grant.OpportunityType.INTERNSHIP, 'Бакалавриат', 29, tech_lab),
            ('Robotics Summer School', 'Летняя школа по робототехнике, embedded-системам и компьютерному зрению.', 'Robotics Academy', 'Япония', 'Инженерия', Grant.OpportunityType.SCHOLARSHIP, 'Бакалавриат', 44, tech_lab),
            ('Climate Journalism Award', 'Конкурс журналистских материалов о климате, устойчивом развитии и городской среде.', 'Climate Media Lab', 'Германия', 'Журналистика', Grant.OpportunityType.CONTEST, 'Бакалавриат', 6, global_fund),
            ('AI for Medicine Program', 'Программа для студентов медицины и IT по применению искусственного интеллекта в диагностике.', 'Health AI Center', 'ОАЭ', 'Медицина', Grant.OpportunityType.GRANT, 'Магистратура', 34, tech_lab),
            ('Entrepreneurship Student Cup', 'Конкурс бизнес-проектов с грантами на запуск студенческих стартапов.', 'Startup Campus', 'США', 'Экономика', Grant.OpportunityType.CONTEST, 'Бакалавриат', 19, tech_lab),
            ('Inclusive Education Fellowship', 'Стипендия для проектов по инклюзивному образованию и цифровым учебным материалам.', 'Open Learning Fund', 'Канада', 'Педагогика', Grant.OpportunityType.SCHOLARSHIP, 'Магистратура', 49, partner),
            ('Cybersecurity Exchange', 'Обменная программа для студентов по кибербезопасности, сетям и защите данных.', 'SecureNet Academy', 'Эстония', 'IT', Grant.OpportunityType.EXCHANGE, 'Бакалавриат, Магистратура', 23, tech_lab),
            ('Renewable Energy Grant', 'Финансирование прототипов и исследований в области солнечной и ветровой энергетики.', 'Energy Transition Fund', 'Норвегия', 'Инженерия', Grant.OpportunityType.GRANT, 'Магистратура', 31, global_fund),
            ('Museum Studies Fellowship', 'Стипендия для студентов искусства, истории и культурного менеджмента.', 'European Museums Network', 'Австрия', 'Искусство', Grant.OpportunityType.SCHOLARSHIP, 'Бакалавриат', 57, partner),
            ('Smart Cities Internship', 'Стажировка в проектах умных городов: транспорт, IoT, урбанистика и данные.', 'Smart City Lab', 'ОАЭ', 'Архитектура', Grant.OpportunityType.INTERNSHIP, 'Магистратура', 28, tech_lab),
            ('Food Security Research Grant', 'Грант для исследований продовольственной безопасности и устойчивых агросистем.', 'Food Future Foundation', 'Италия', 'Агронаука', Grant.OpportunityType.GRANT, 'Магистратура', 40, global_fund),
            ('Human Rights Essay Contest', 'Международный конкурс эссе для студентов права и социальных наук.', 'Human Rights Forum', 'Франция', 'Право', Grant.OpportunityType.CONTEST, 'Бакалавриат', 13, partner),
            ('Digital Humanities School', 'Краткосрочная образовательная программа по цифровым методам в гуманитарных науках.', 'Digital Humanities Lab', 'Польша', 'Социальные науки', Grant.OpportunityType.EXCHANGE, 'Бакалавриат', 46, global_fund),
        ]

        grants = {}
        for title, description, organization, country, category, kind, level, days, created_by in demo_grants:
            grant, _ = Grant.objects.update_or_create(
                title=title,
                defaults={
                    'description': description,
                    'organization': organization,
                    'country': country,
                    'category': categories[category],
                    'opportunity_type': kind,
                    'education_level': level,
                    'requirements': (
                        'Хорошая академическая успеваемость; мотивационное письмо; '
                        'знание английского языка не ниже B1/B2; соответствие направлению программы.'
                    ),
                    'documents': (
                        'CV, мотивационное письмо, академическая справка, копия паспорта, '
                        'сертификаты и портфолио при наличии.'
                    ),
                    'deadline': today + timedelta(days=days),
                    'official_link': f'https://example.org/{title.lower().replace(" ", "-")}',
                    'created_by': created_by,
                },
            )
            grants[title] = grant

        return grants

    def create_student_activity(self, users, grants):
        student = users['student@granthub.local']
        timur = users['timur.student@granthub.local']
        madina = users['madina.student@granthub.local']
        aziz = users['aziz.student@granthub.local']

        saved_map = {
            student: ['Global Tech Scholarship 2026', 'Data Science Bootcamp Grant', 'Cybersecurity Exchange', 'Entrepreneurship Student Cup'],
            timur: ['Young Engineers Challenge', 'Robotics Summer School', 'Renewable Energy Grant', 'Smart Cities Internship'],
            madina: ['Medical Research Mobility', 'AI for Medicine Program', 'Biotech Research Grant'],
            aziz: ['Economics for Development', 'FinTech Internship Asia', 'Entrepreneurship Student Cup'],
        }
        for user, titles in saved_map.items():
            for title in titles:
                SavedGrant.objects.get_or_create(user=user, grant=grants[title])

        application_map = [
            (student, 'Global Tech Scholarship 2026', Application.Status.REVIEW),
            (student, 'Startup Internship Europe', Application.Status.APPROVED),
            (timur, 'Young Engineers Challenge', Application.Status.REVIEW),
            (timur, 'Renewable Energy Grant', Application.Status.REJECTED),
            (madina, 'Medical Research Mobility', Application.Status.APPROVED),
            (madina, 'AI for Medicine Program', Application.Status.REVIEW),
            (aziz, 'Economics for Development', Application.Status.REVIEW),
            (aziz, 'FinTech Internship Asia', Application.Status.APPROVED),
        ]
        for user, title, status in application_map:
            Application.objects.update_or_create(
                user=user,
                grant=grants[title],
                defaults={'status': status},
            )

        notifications = {
            student: [
                'Добро пожаловать в GrantHub! Заполните профиль для получения точных рекомендаций.',
                'Скоро дедлайн по программе Data Science Bootcamp Grant.',
                'Статус заявки на Startup Internship Europe изменен: одобрено.',
            ],
            timur: [
                'Новая программа подходит вашему профилю: Robotics Summer School.',
                'Скоро дедлайн по конкурсу Young Engineers Challenge.',
            ],
            madina: [
                'Вам может подойти программа AI for Medicine Program.',
                'Статус заявки на Medical Research Mobility изменен: одобрено.',
            ],
            aziz: [
                'Новая возможность по экономике: FinTech Internship Asia.',
                'Скоро дедлайн конкурса Entrepreneurship Student Cup.',
            ],
        }
        for user, messages in notifications.items():
            for message in messages:
                Notification.objects.get_or_create(user=user, message=message)
