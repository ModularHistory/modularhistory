import os
import sys
from glob import glob

import django
from decouple import config
from django.core import management
from paramiko import SSHClient
from scp import SCPClient

# Initialize Django
print('Initializing Django...')
my_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(my_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'history.settings')
django.setup()

from history import settings


# from history import settings
# from django.db import transaction
# from django.contrib.auth.models import Permission, Group
# from django.contrib.contenttypes.models import ContentType
# from sources.models import Citation, QSR, OSR, Source


if not settings.DEBUG:
    print(f'Backing up database....')
    # Create backup file
    # management.call_command('dbbackup')
    # Select latest backup file
    os.chdir(os.path.join(f'{settings.BASE_DIR}', 'history/backups/'))
    files = glob('*sql')  # .psql or .sql files
    if not files:
        print(f'Could not find a db backup file.')
    backup_file = max(files, key=os.path.getmtime)
    # Connect to remote backup server
    server = config('REMOTE_BACKUP_SERVER', default=None)
    username = config('REMOTE_BACKUP_SERVER_USERNAME', default=None)
    password = config('REMOTE_BACKUP_SERVER_PASSWORD', default=None)
    ssh_client = SSHClient()
    ssh_client.load_system_host_keys()
    # ssh_client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    if server:
        print(f'Connecting to remote backup location: {server}')
        ssh_client.connect(server, username=username, password=password)
        print('Connected.')
        # ssh_client.connect(server, username='username', password='password')
        with SCPClient(ssh_client.get_transport()) as scp_client:
            scp_client.put(backup_file, f'~/history/history/backups/{backup_file}')
            # scp_client.get('test2.txt')
        print(f'Completed remote db backup.')

