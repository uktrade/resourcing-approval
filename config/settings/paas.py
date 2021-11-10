from .base import env


# HSTS
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# django-storages
# https://django-storages.readthedocs.io/en/latest/
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# django-chunk-upload-handlers
# https://github.com/uktrade/django-chunk-s3-av-upload-handlers
FILE_UPLOAD_HANDLERS = (
    # "django_chunk_upload_handlers.clam_av.ClamAVFileUploadHandler",
    "django_chunk_upload_handlers.s3.S3FileUploadHandler",
)  # Order is important

# AWS S3
AWS_REGION_NAME = env("AWS_REGION_NAME")
AWS_S3_REGION_NAME = AWS_REGION_NAME
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_QUERYSTRING_EXPIRE = 60 * 5  # 5 minutes in seconds
