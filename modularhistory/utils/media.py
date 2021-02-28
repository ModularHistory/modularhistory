from glob import glob
from os.path import join
from typing import Optional

from decouple import config
from django.conf import settings
from invoke.context import Context

from modularhistory.constants.environments import Environments
from modularhistory.utils.files import upload_to_mega

CONTEXT = Context()
DAYS_TO_KEEP_BACKUP = 7
SECONDS_IN_DAY = 86400
SECONDS_TO_KEEP_BACKUP = DAYS_TO_KEEP_BACKUP * SECONDS_IN_DAY


def back_up(
    context: Context = CONTEXT,
    redact: bool = False,
    push: bool = False,
    filename: Optional[str] = None,
):
    """Create a media backup file."""
    backups_dir, media_dir = settings.BACKUPS_DIR, settings.MEDIA_ROOT
    backup_files_pattern = join(backups_dir, '*.tar.gz')
    account_media_dir = join(media_dir, 'account')
    temp_dir = join(settings.BASE_DIR, 'account_media')
    exclude_account_media = redact and os.path.exists(account_media_dir)
    if exclude_account_media:
        context.run(f'mv {account_media_dir} {temp_dir}')
        context.run(f'mkdir {account_media_dir}')
    # https://github.com/django-dbbackup/django-dbbackup#mediabackup
    context.run('python manage.py mediabackup -z --noinput', hide='out')
    if exclude_account_media:
        context.run(f'rm -r {account_media_dir}')
        context.run(f'mv {temp_dir} {account_media_dir}')
    backup_files = glob(backup_files_pattern)
    backup_file = max(backup_files, key=os.path.getctime)
    if filename:
        context.run(f'mv {backup_file} {join(backups_dir, filename)}')
        backup_file = join(backups_dir, filename)
    print(f'Finished creating backup file: {backup_file}')
    if push:
        upload_to_mega(file=backup_file, account=Environments.DEV)


def sync(context: Context = CONTEXT, push: bool = False, max_transfer: str = '5G'):
    """Sync media from source to destination, modifying destination only."""
    # TODO: refactor
    use_gdrive = True
    local_media_dir = settings.MEDIA_ROOT
    remote_media_dir = 'gdrive:/media/' if use_gdrive else 'mega:/media/'
    if push:
        source, destination = (local_media_dir, remote_media_dir)
    else:
        source, destination = (remote_media_dir, local_media_dir)
    command = (
        f'rclone sync {source} {destination} '
        # https://rclone.org/flags/
        f'--max-transfer={max_transfer} --order-by="size,ascending" --progress '
        f'--config {join(settings.BASE_DIR, "config/rclone/rclone.conf")}'
    )
    if use_gdrive:
        credentials = config('RCLONE_GDRIVE_SA_CREDENTIALS')
        # https://rclone.org/drive/#standard-options
        command = (
            f"{command} --drive-service-account-credentials='{credentials}' "
            '--drive-use-trash=false'
        )
    else:
        mega_username = config(
            'MEGA_DEV_USERNAME', default=config('MEGA_USERNAME', default=None)
        )
        mega_password = config(
            'MEGA_DEV_PASSWORD', default=config('MEGA_PASSWORD', default=None)
        )
        command = (
            f'{command} --mega-user={mega_username} '
            f'--mega-pass=$(echo "{mega_password}" | rclone obscure -)'
        )
    if push:
        command = f'{command} --drive-stop-on-upload-limit'
        context.run(f'echo "" && {command} --dry-run; echo ""')
        print('Completed dry run. Proceeding shortly ...')
        context.run('sleep 10')
    else:
        command = f'{command} --drive-stop-on-download-limit'
    context.run(command)
