import json

from countries.management.commands.generate_countries_fixture import Command


TEST_JSON = """
{
  "data": [
    {
      "reference_id": "ZZZZZZ00001",
      "name": "Country 1",
      "type": "Territory",
      "iso1_code": "",
      "iso2_code": "",
      "iso3_code": "",
      "overseas_region_overseas_region_name": "Somewhere",
      "start_date": null,
      "end_date": null,
      "region": "Somewhere"
    },
    {
      "reference_id": "ZZZZZZ00002",
      "name": "Country 2",
      "type": "Country",
      "iso1_code": "00Z",
      "iso2_code": "ZZ",
      "iso3_code": "ZZZ",
      "overseas_region_overseas_region_name": "Somewhere Else",
      "start_date": "1990-01-01",
      "end_date": "2022-01-01",
      "region": "Somewhere Else"
    }
  ]
}
"""
TEST_SRC_DATA = json.loads(TEST_JSON)["data"]


def test_generate_fixture_data():
    fixture_data = Command._generate_fixture_data(TEST_SRC_DATA)

    assert fixture_data == [
        {
            "model": "countries.Country",
            "pk": "ZZZZZZ00002",
            "fields": {
                "name": "Country 2",
                "iso_1_code": "00Z",
                "iso_2_code": "ZZ",
                "iso_3_code": "ZZZ",
                "overseas_region": "Somewhere Else",
                "start_date": "1990-01-01",
                "end_date": "2022-01-01",
            },
        }
    ]
