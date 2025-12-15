from .models import Notification


def notifications_unread_count(request):
    """Adiciona `notifications_unread_count` ao contexto das templates.

    Retorna 0 para usuários anônimos.
    """
    count = 0
    try:
        if request.user and request.user.is_authenticated:
            count = Notification.objects.filter(user=request.user, read=False).count()
    except Exception:
        count = 0
    return {'notifications_unread_count': count}
