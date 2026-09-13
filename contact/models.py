from django import forms
from django.conf import settings
from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet


class ContactFormField(AbstractFormField):
    page = ParentalKey("contact.ContactPage", on_delete=models.CASCADE, related_name="form_fields")


class ContactPage(AbstractEmailForm):
    """
    The contact page. Built on Wagtail's form builder (AbstractEmailForm)
    so an editor can add/reorder/remove fields from the admin — e.g. add a
    "Société" field for B2B enquiries — without touching code, and every
    submission is stored (visible under Forms > Contact in the admin) as
    well as emailed to `to_address`.
    """

    intro = RichTextField(blank=True, features=["bold", "italic", "link"])
    thank_you_text = RichTextField(
        blank=True,
        default="<p>Merci, votre message a bien été envoyé. Notre équipe vous répondra rapidement.</p>",
    )

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Champs du formulaire"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel([FieldPanel("from_address"), FieldPanel("to_address")]),
                FieldPanel("subject"),
            ],
            "Notification par e-mail",
        ),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["site_settings_email"] = getattr(settings, "CONTACT_FORM_RECIPIENT_EMAIL", "")
        return context

    # --- Invisible honeypot spam trap ---------------------------------
    # A "website" field, hidden with CSS (.form-honeypot in components.css)
    # and never shown to editors in the panel builder. Real visitors never
    # fill it in; bots that auto-fill every field do, and get silently
    # dropped in process_form_submission instead of a visible rejection —
    # that keeps automated spam scripts from learning to route around it.
    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["website"] = forms.CharField(required=False, label="")
        return form

    def process_form_submission(self, form):
        if form.cleaned_data.get("website"):
            return None
        form.cleaned_data.pop("website", None)
        return super().process_form_submission(form)

    class Meta:
        verbose_name = "Page « Contact »"


@register_snippet
class NewsletterSubscriber(models.Model):
    """Plain e-mail capture from the footer newsletter form (no 3rd-party ESP wired up yet)."""

    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [FieldPanel("email")]

    class Meta:
        verbose_name = "Abonné newsletter"
        verbose_name_plural = "Abonnés newsletter"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
