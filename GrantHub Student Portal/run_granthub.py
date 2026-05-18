import os
import socket
import threading
import webbrowser
from pathlib import Path

import django
from django.core.management import call_command, execute_from_command_line


def find_free_port(start=8000, limit=20):
    for port in range(start, start + limit):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start


def prepare_database():
    django.setup()
    call_command('migrate', interactive=False, verbosity=0)

    from portal.models import Grant

    if Grant.objects.count() == 0:
        call_command('seed_demo', verbosity=0)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    Path('media').mkdir(exist_ok=True)
    prepare_database()

    port = find_free_port()
    url = f'http://127.0.0.1:{port}/'
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    print('GrantHub Student Portal запущен.')
    print(f'Откройте в браузере: {url}')
    print('Для остановки закройте это окно или нажмите Ctrl+C.')

    execute_from_command_line(['manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload'])


if __name__ == '__main__':
    main()
