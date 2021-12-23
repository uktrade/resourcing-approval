from typing import Any

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select


def copy_database(source: str, target: str, db_settings: dict[str, Any]) -> None:
    """Copy a database using the source as a template.

    Args:
        source: The template database.
        target: The target database to be created.
        db_settings: Database connection settings.
    """
    run_sql(f'DROP DATABASE IF EXISTS "{target}"', db_settings)
    run_sql(
        f'CREATE DATABASE "{target}" WITH TEMPLATE "{source}"',
        db_settings,
    )


def delete_database(database: str, db_settings: dict[str, Any]) -> None:
    """Delete a database if it exists.

    Args:
        database: The database to be deleted.
        db_settings: Database connection settings.
    """
    run_sql(f'DROP DATABASE IF EXISTS "{database}"', db_settings)


def run_sql(sql: str, db_settings: dict[str, Any]) -> None:
    """Run the SQL query on PostgreSQL  bypassing the Django ORM.

    Args:
        sql: The query to be ran.
        db_settings: A dict of database connection settings.
    """
    conn = psycopg2.connect(
        host=db_settings["HOST"],
        port=db_settings["PORT"],
        user=db_settings["USER"],
        password=db_settings["PASSWORD"],
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(sql)
    conn.close()


def fill_out_form(driver: WebDriver, form: WebElement, **form_data):
    for name, value in form_data.items():
        set_element_value(driver, form.find_element_by_name(name), value)


def set_element_value(driver: WebDriver, element: WebElement, value: Any):
    value = str(value)

    if element.tag_name == "input":
        if element.get_attribute("type") == "date":
            # TODO: Ideally we would not have to reach for javascript to handle dates.
            driver.execute_script(
                f"document.querySelector('input[name={element.get_attribute('name')}]').value = '{value}';"
            )
        else:
            element.clear()
            element.send_keys(value)
    elif element.tag_name == "select":
        select = Select(element)
        select.select_by_value(value)
    else:
        raise TypeError(f"Unsupported type of element {element.tag_name!r}")
