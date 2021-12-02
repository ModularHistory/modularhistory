import os
from glob import glob
from os.path import join
from typing import Optional

from decouple import config
from django.conf import settings
from invoke.context import Context

from core.constants.environments import Environments
from core.constants.misc import RcloneStorageProviders

CONTEXT = Context()
DAYS_TO_KEEP_BACKUP = 7
SECONDS_IN_DAY = 86400
SECONDS_TO_KEEP_BACKUP = DAYS_TO_KEEP_BACKUP * SECONDS_IN_DAY


def backup(
    context: Context = CONTEXT,
    redact: bool = False,
    push: bool = False,
    filename: Optional[str] = None,
):
    """Create a media backup file."""
    backups_dir, media_dir = settings.BACKUPS_DIR, settings.MEDIA_ROOT
    backup_files_pattern = join(backups_dir, '*.tar.gz')
    users_media_dir = join(media_dir, 'users')
    temp_dir = join(settings.BASE_DIR, 'users_media')
    exclude_users_media = redact and os.path.exists(users_media_dir)
    if exclude_users_media:
        context.run(f'mv {users_media_dir} {temp_dir}')
        context.run(f'mkdir {users_media_dir}')
    # https://github.com/django-dbbackup/django-dbbackup#mediabackup
    context.run('python manage.py mediabackup -z --noinput', hide='out')
    if exclude_users_media:
        context.run(f'rm -r {users_media_dir}')
        context.run(f'mv {temp_dir} {users_media_dir}')
    backup_files = glob(backup_files_pattern)
    backup_file = max(backup_files, key=os.path.getctime)
    if filename:
        context.run(f'mv {backup_file} {join(backups_dir, filename)}')
        backup_file = join(backups_dir, filename)
    print(f'Finished creating backup file: {backup_file}')
    # if push:
    #     upload_to_mega(backup_file, account=Environments.DEV)


RCLONE_STORAGE_PROVIDERS = (
    RcloneStorageProviders.GOOGLE_DRIVE,
    RcloneStorageProviders.MEGA,
)


def sync(
    context: Context = CONTEXT,
    push: bool = False,
    storage_provider: str = RcloneStorageProviders.GOOGLE_DRIVE,
):
    """Sync media from source to destination, modifying destination only."""
    if storage_provider not in RCLONE_STORAGE_PROVIDERS:
        raise ValueError(f'Unknown storage provider: {storage_provider}')
    local_media_dir = settings.MEDIA_ROOT
    remote_media_dir = f'{storage_provider}:/media/'
    if push:
        source, destination = (local_media_dir, remote_media_dir)
    else:
        source, destination = (remote_media_dir, local_media_dir)
    command = (
        f'rclone sync {source} {destination} '
        # https://rclone.org/flags/
        f'--config {join(settings.CONFIG_DIR, "rclone/rclone.conf")} '
        f'--exclude-from {join(settings.CONFIG_DIR, "rclone/filters.txt")} '
        f'--order-by="size,ascending" --progress'
    )
    if storage_provider == RcloneStorageProviders.GOOGLE_DRIVE:
        credentials = config('RCLONE_GDRIVE_SA_CREDENTIALS')
        # https://rclone.org/drive/#standard-options
        command = (
            f"{command} --drive-service-account-credentials='{credentials}' "
            '--drive-use-trash=false'
        )
    elif storage_provider == RcloneStorageProviders.MEGA:
        mega_username = config('MEGA_USERNAME', default=None)
        mega_password = config('MEGA_PASSWORD', default=None)
        command = (
            f'{command} --max-transfer=5G '
            f'--mega-user={mega_username} '
            f'--mega-pass=$(echo "{mega_password}" | rclone obscure -)'
        )
    else:
        raise NotImplementedError(f'Syncing media with {storage_provider} is not supported.')
    if push:
        command = f'{command} --drive-stop-on-upload-limit'
        context.run(f'echo "" && {command} --dry-run; echo ""')
        print('Completed dry run. Proceeding shortly ...')
        context.run('sleep 10')
    else:
        command = f'{command} --drive-stop-on-download-limit'
    context.run(command)
