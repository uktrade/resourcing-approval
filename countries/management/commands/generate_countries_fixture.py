import json
from operator import itemgetter
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate a fixture of country data from the Data Workspace dataset"

    def add_arguments(self, parser):
        parser.add_argument("src", type=Path)

    def handle(self, *args, **options):
        src: Path = options["src"]

        with src.open() as f:
            # There should be a top level "data" key.
            src_data = json.load(f)["data"]

        fixture_data = self._generate_fixture_data(src_data)

        self.stdout.write(json.dumps(fixture_data, indent=2))

    @classmethod
    def _generate_fixture_data(cls, src_data):
        return sorted(
            (
                fixture_obj
                for obj in src_data
                if (fixture_obj := cls._generate_fixture_obj(obj))
            ),
            key=itemgetter("pk"),
        )

    @staticmethod
    def _generate_fixture_obj(obj):
        if obj["type"] != "Country":
            return None

        return {
            "model": "countries.Country",
            "pk": obj["reference_id"],
            "fields": {
                "name": obj["name"],
                "iso_1_code": obj["iso1_code"],
                "iso_2_code": obj["iso2_code"],
                "iso_3_code": obj["iso3_code"],
                "overseas_region": obj["overseas_region_overseas_region_name"],
                "start_date": obj["start_date"],
                "end_date": obj["end_date"],
            },
        }
