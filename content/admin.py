from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "status", "created_by", "created_at"
    )
    list_filter = ("status", "created_at")
    search_fields = ("title", "content", "slug")
    prepopulated_fields = {"slug": ("title",)}