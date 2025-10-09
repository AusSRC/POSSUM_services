from django.apps import AppConfig


class PipelineValidationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'processing_states'
    verbose_name = 'Processing States'
