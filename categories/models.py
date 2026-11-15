from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True,null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# name: Unique category name.
# description: Optional explanation of the category.
# active: Allows administrators to activate/deactivate categories without deleting them.
# created_at: Automatically stores creation time.
# updated_at: Automatically stores the latest update time.