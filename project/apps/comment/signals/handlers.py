from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from project.apps.comment.exceptions import CommentTreeException
from project.apps.comment.models import Comment, CommentTree


@receiver(pre_delete, sender=Comment)
def delete_comments_tree_handler(sender, instance, **kwargs):
    if instance.__class__.objects.filter(parent=instance.pk).exists():
        raise CommentTreeException
    CommentTree.objects.filter(descendant=instance.pk)


@receiver(post_save, sender=Comment)
def create_comments_tree_handler(sender, instance, created, **kwargs):
    if created:
        to_save = [CommentTree(
            ancestor=instance,
            descendant=instance,
            depth=0
        )]
        if instance.parent:
            nodes = CommentTree.objects.select_related(
                'ancestor'
            ).filter(
                descendant=instance.parent
            )
            for row in nodes:
                to_save.append(CommentTree(
                    ancestor=row.ancestor,
                    descendant=instance,
                    depth=row.depth + 1
                ))
        CommentTree.objects.bulk_create(to_save)
