from django.conf import settings
from django.core.management.base import BaseCommand

from main.services.resourcing_request import create_full_test_resourcing_request


class Command(BaseCommand):
    help = "Create a test resourcing request"

    def add_arguments(self, parser):
        parser.add_argument("--job-title", default="Python Developer")
        parser.add_argument("--project-name", default="Testing")
        parser.add_argument("--inside-ir35", default=True)

    def handle(self, *args, **options):
        assert settings.APP_ENV in (
            "local",
            "dev",
        ), "Command can only be ran in a dev environment"

        create_full_test_resourcing_request(
            job_title=options["job_title"],
            project_name=options["project_name"],
            inside_ir35=options["inside_ir35"] == "True",
        )

        self.stdout.write(
            self.style.SUCCESS("Successfully created test resourcing request")
        )
