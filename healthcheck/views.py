"""
https://readme.trade.gov.uk/docs/howtos/healthcheck.html#healthcheckpattern
"""

from django.conf import settings
from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse
from redis import Redis
from redis.exceptions import RedisError


# https://documentation.solarwinds.com/en/success_center/pingdom/content/topics/http-custom-check.htm?cshid=pd-rd_115000431709-http-custom-check
PINGDOM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<pingdom_http_custom_check>
    <status>{status}</status>
</pingdom_http_custom_check>
"""


def healthcheck(request):
    ok = True

    # Check the database service.
    try:
        connection.ensure_connection()
    except OperationalError:
        ok = False

    # Without a results backend we can't check the celery service.

    # Check the redis service.
    try:
        r = Redis.from_url(settings.CELERY_BROKER_URL)
        r.info()
        r.close()
    except RedisError:
        ok = False

    status = "OK" if ok else "FAILED"
    status_code = 200 if ok else 503

    return HttpResponse(
        PINGDOM_XML.format(status=status),
        status=status_code,
        content_type="text/xml",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )
