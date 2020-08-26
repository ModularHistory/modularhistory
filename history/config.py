import os

from decouple import Config, AutoConfig, RepositoryEmpty as Repository

IS_GCP = bool(os.getenv('GAE_APPLICATION', None))

if IS_GCP:
    from google.cloud.secretmanager import SecretManagerServiceClient

PROJECT_ID = 'modularhistory'


class GoogleSecretRepository(Repository):
    def __init__(self, source=''):
        super().__init__(self, source)
        self.secrets = {}
        self.client = SecretManagerServiceClient()
        # Build the parent name from the project.
        parent = self.client.project_path(PROJECT_ID)
        for element in self.client.list_secrets(parent):
            if hasattr(element, 'name'):
                key = element.name.split('/secrets/')[-1]
                name = self.client.secret_version_path(PROJECT_ID, key, 'latest')
                try:
                    # Access the secret.
                    response = self.client.access_secret_version(name)
                    payload = response.payload.data.decode('UTF-8')
                    self.secrets[key] = payload
                except Exception as e:
                    print(f'{type(e): {e}}')
            else:
                print(f'{type(element)}')

    def __contains__(self, key):
        return key in os.environ or key in self.secrets

    def __getitem__(self, key):
        return self.secrets.get(key, None)


class ModularHistoryAutoConfig(AutoConfig):
    def __call__(self, *args, **kwargs):
        if IS_GCP and not self.config:
            super().__call__(*args, **kwargs)
            default_repository = self.config.repository
            repository = GoogleSecretRepository()
            for key in default_repository.data:
                if key not in repository:
                    repository.secrets[key] = default_repository[key]
            self.config = Config(repository)
        return super().__call__(*args, **kwargs)


config = ModularHistoryAutoConfig()
