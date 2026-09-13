from django.db import models
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from core.blocks import BodyStreamBlock


class NewsIndexPage(Page):
    intro = RichTextField(blank=True, features=["bold", "italic", "link"])

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["news.NewsPage"]
    parent_page_types = ["home.HomePage"]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        articles = self.get_children().live().order_by("-first_published_at").specific()

        tag = request.GET.get("tag")
        if tag:
            articles = [a for a in articles if tag in [t.name for t in a.tags.all()]]

        paginator = Paginator(articles, 9)
        page_number = request.GET.get("page")
        try:
            articles_page = paginator.page(page_number)
        except PageNotAnInteger:
            articles_page = paginator.page(1)
        except EmptyPage:
            articles_page = paginator.page(paginator.num_pages)

        context["articles"] = articles_page
        context["active_tag"] = tag
        return context

    class Meta:
        verbose_name = "Page « Actualités »"


class NewsPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "news.NewsPage", related_name="tagged_items", on_delete=models.CASCADE,
    )


class NewsPage(Page):
    date = models.DateField("Date de publication")
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    excerpt = models.CharField(max_length=280)
    body = StreamField(BodyStreamBlock(), blank=True, use_json_field=True)
    tags = ClusterTaggableManager(through=NewsPageTag, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("excerpt"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("cover_image"),
        FieldPanel("excerpt"),
        FieldPanel("tags"),
        FieldPanel("body"),
    ]

    parent_page_types = ["news.NewsIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Article d'actualité"
        verbose_name_plural = "Articles d'actualité"
        ordering = ["-date"]
