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
