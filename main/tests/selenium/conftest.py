import pytest
from django.db import connections

from .utils import copy_database, delete_database


TEMPLATE_DB_PREFIX = "template_"
SELENIUM_DB_PREFIX = "selenium_"


@pytest.fixture(scope="package", autouse=True)
def django_db_setup(django_db_setup):
    from django.conf import settings

    db_settings = settings.DATABASES["default"]
    test_db_name = db_settings["NAME"]
    template_db_name = TEMPLATE_DB_PREFIX + db_settings["NAME"]
    selenium_db_name = SELENIUM_DB_PREFIX + db_settings["NAME"]

    # We need to close all the connections to avoid errors when copying the database.
    for connection in connections.all():
        connection.close()

    # Create the template database.
    copy_database(
        source=db_settings["NAME"],
        target=template_db_name,
        db_settings=db_settings,
    )

    # Point the django settings at our new database.
    settings.DATABASES["default"]["NAME"] = selenium_db_name

    # Let the tests in the package run.
    yield

    # Delete the selenium test database.
    delete_database(database=selenium_db_name, db_settings=db_settings)
    # Delete the template database.
    delete_database(database=template_db_name, db_settings=db_settings)

    # Reset the django settings.
    settings.DATABASES["default"]["NAME"] = test_db_name


@pytest.fixture(scope="function", autouse=True)
def copy_template_db():
    from django.conf import settings

    db_settings = settings.DATABASES["default"]
    selenium_db_name = db_settings["NAME"]
    test_db_name = selenium_db_name.removeprefix(SELENIUM_DB_PREFIX)
    template_db_name = TEMPLATE_DB_PREFIX + test_db_name

    # We need to close all the connections to avoid errors when copying the database.
    for connection in connections.all():
        connection.close()

    # Create a new selenium test database from the template database.
    copy_database(
        source=template_db_name,
        target=selenium_db_name,
        db_settings=db_settings,
    )
