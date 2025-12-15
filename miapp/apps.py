from django.apps import AppConfig


class MiappConfig(AppConfig):
    """
    Configuración de la aplicación Django.

    Esta clase define la configuración principal de la aplicación,
    incluyendo el nombre de la app y el tipo de campo automático
    utilizado para las claves primarias.

    Django application configuration.

    This class defines the main configuration of the application,
    including the app name and the default automatic field type
    used for primary keys.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'miapp'
