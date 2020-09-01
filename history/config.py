# import os

from decouple import AutoConfig  # , Config, RepositoryEmpty as Repository

# IS_GCP = bool(os.getenv('GAE_APPLICATION', None))
#
# if IS_GCP:
#     from google.cloud.secretmanager import SecretManagerServiceClient

PROJECT_ID = 'modularhistory'


# class SecretRepository(Repository):
#     def __init__(self, source=''):
#         super().__init__(self, source)
#         self.secrets = {}
#
#         # Get secrets from Google
#         client = SecretManagerServiceClient()
#         parent = client.project_path(PROJECT_ID)  # Build the parent name from the project
#         for element in client.list_secrets(parent):
#             if hasattr(element, 'name'):
#                 key = element.name.split('/secrets/')[-1]
#                 name = client.secret_version_path(PROJECT_ID, key, 'latest')
#                 try:
#                     # Access the secret.
#                     response = client.access_secret_version(name)
#                     payload = response.payload.data.decode('UTF-8')
#                     self.secrets[key] = payload
#                 except Exception as e:
#                     print(f'{type(e): {e}}')
#
#     def __contains__(self, key):
#         return key in os.environ or key in self.secrets
#
#     def __getitem__(self, key):
#         return self.secrets.get(key, None)


class ModularHistoryAutoConfig(AutoConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # def __call__(self, *args, **kwargs):
    #     if not self.config:
    #         super().__call__(*args, **kwargs)
    #         repository = SecretRepository()
    #         env_vars = self.config.repository.data
    #         for key in env_vars:
    #             if key not in repository.secrets:
    #                 repository.secrets[key] = env_vars[key]
    #         self.config = Config(repository)
    #     return super().__call__(*args, **kwargs)


config: ModularHistoryAutoConfig = ModularHistoryAutoConfig()
