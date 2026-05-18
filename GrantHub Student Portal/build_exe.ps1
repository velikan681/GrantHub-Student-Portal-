$ErrorActionPreference = "Stop"

python manage.py check
python manage.py migrate
python manage.py seed_demo

pyinstaller `
  --noconfirm `
  --onedir `
  --name "GrantHubStudentPortal" `
  --add-data "portal/templates;portal/templates" `
  --add-data "portal/static;portal/static" `
  --add-data "db.sqlite3;." `
  --collect-submodules "portal.migrations" `
  --collect-submodules "django.contrib.admin.migrations" `
  --collect-submodules "django.contrib.auth.migrations" `
  --collect-submodules "django.contrib.contenttypes.migrations" `
  --collect-submodules "django.contrib.sessions.migrations" `
  --hidden-import "portal.management.commands.seed_demo" `
  run_granthub.py

Write-Host ""
Write-Host "EXE готов: dist\GrantHubStudentPortal\GrantHubStudentPortal.exe"
