from django.db import models


class CommentManager(models.QuerySet):
    def get_descendants(self, ancestor_id, include_self=False):
        queryset = self.filter(
            comment_tree_descendant__ancestor=ancestor_id
        )
        if not include_self:
            queryset = queryset.exclude(pk=ancestor_id)
        return queryset

    def get_grand_parents(self, **filter_kwargs):
        return self.filter(parent=None, **filter_kwargs).annotate(
            children_cnt=models.Count('comment_tree_ancestor__id') - 1
        )
