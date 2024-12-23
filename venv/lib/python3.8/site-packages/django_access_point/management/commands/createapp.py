import os
import importlib.resources
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Creates a Django app directory structure for the given app name and custom files"

    package_name = 'django_access_point'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='Name of the app to create')

    def handle(self, *args, **options):
        app_name = options['app_name']  # Get the app name from the options
        app_path = os.path.join(os.getcwd(), app_name)

        if os.path.exists(app_path):
            raise CommandError(f'App "{app_name}" already exists.')

        # Create the app directory structure
        os.makedirs(app_path)
        self.create_init_file(app_path)
        self.create_model_file(app_path)
        self.create_serializer_file(app_path)
        self.create_url_file(app_path)
        self.create_view_file(app_path)
        self.create_auth_view_file(app_path)
        self.create_email_template_files(app_path)
        self.create_command_files(app_path)

        self.stdout.write(self.style.SUCCESS(f'App "{app_name}" created successfully!'))

    def create_init_file(self, app_path):
        self.create_file(app_path, '__init__.py', '')

    def create_model_file(self, app_path):
        self.create_file(app_path, 'models.py', 'app_models.py')

    def create_serializer_file(self, app_path):
        self.create_file(app_path, 'serializers.py', 'app_serializers.py')

    def create_url_file(self, app_path):
        self.create_file(app_path, 'urls.py', 'app_urls.py')

    def create_view_file(self, app_path):
        self.create_file(app_path, 'views.py', 'app_views.py')

    def create_auth_view_file(self, app_path):
        self.create_file(app_path, 'auth.py', 'app_auth.py')

    def create_email_template_files(self, app_path):
        templates_path = os.path.join(app_path, 'templates')
        os.makedirs(templates_path, exist_ok=True)

        self.create_file(templates_path, 'password_reset_email.html', 'app_password_reset_email.html')
        self.create_file(templates_path, 'profile_invite_email.html', 'app_profile_invite_email.html')

    def create_command_files(self, app_path):
        management_path = os.path.join(app_path, 'management')
        commands_path = os.path.join(app_path, "management", 'commands')
        os.makedirs(management_path, exist_ok=True)
        os.makedirs(commands_path, exist_ok=True)

        self.create_file(management_path, '__init__.py', '')
        self.create_file(commands_path, '__init__.py', '')
        self.create_file(commands_path, 'create_portal_admin_user.py', 'app_create_portal_admin_user.py')

    def create_file(self, app_path, file_name, source_file_name):
        package_name = self.package_name

        file_content = ""

        # Read the source content
        if source_file_name:
            try:
                file_content = importlib.resources.read_text(package_name, source_file_name)
            except FileNotFoundError:
                raise CommandError(f'The specified source file "{source_file_name}" in the package "{package_name}" could not be found.')

        # Create the file in the new app
        file_path = os.path.join(app_path, file_name)
        with open(file_path, 'w') as file:
            file.write(file_content)