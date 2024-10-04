from django.conf import settings
from django.templatetags.static import static

def static_context(request):
    return {
        'static': static,
        'STATIC_URL': settings.STATIC_URL,
    }
