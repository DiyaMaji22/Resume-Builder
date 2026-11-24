from django.apps import AppConfig
from django.urls import register_converter


class CoreConfig(AppConfig):
    name = "core"
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"

    def ready(self) -> None:
        from core.converters import ObjectIdConverter

        register_converter(ObjectIdConverter, "oid")
