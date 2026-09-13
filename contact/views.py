from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from contact.models import NewsletterSubscriber


@require_POST
def newsletter_subscribe(request):
    email = request.POST.get("email", "").strip()
    redirect_to = request.META.get("HTTP_REFERER", "/")

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, "Merci de saisir une adresse e-mail valide.")
        return redirect(redirect_to)

    NewsletterSubscriber.objects.get_or_create(email=email)
    messages.success(request, "Merci ! Vous êtes inscrit(e) à notre newsletter.")
    return redirect(redirect_to)
