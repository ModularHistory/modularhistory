"""
Based on https://github.com/worsht/django-dag-postgresql/blob/master/django_dag_postgresql/models.py.

A class to model hierarchies of objects following Directed Acyclic Graph structure.

The graph traversal queries use Postgresql's recursive CTEs to fetch an entire tree
of related node ids in a single query. These queries also topologically sort the ids
by generation.

Inspired by:
https://www.fusionbox.com/blog/detail/graph-algorithms-in-a-database-recursive-ctes-and-topological-sort-with-postgres/620/
https://github.com/elpaso/django-dag
https://github.com/stdbrouw/django-treebeard-dag
"""

from abc import abstractmethod
from typing import TYPE_CHECKING, Optional, Union

from django.core.exceptions import ValidationError
from django.db import connection, models
from django.db.models import Case, When
from django.db.models.base import Model

from core.models.abstract import AbstractModel
from core.models.model import ExtendedModel
from core.models.relations.relation import Relation

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


ANCESTOR_QUERY = '''
WITH RECURSIVE traverse(id, depth) AS (
    SELECT first.parent_id, 1
        FROM {relationship_table} AS first
        LEFT OUTER JOIN {relationship_table} AS second
        ON first.parent_id = second.child_id
    WHERE first.child_id = %(id)s
UNION
    SELECT DISTINCT parent_id, traverse.depth + 1
        FROM traverse
        INNER JOIN {relationship_table}
        ON {relationship_table}.child_id = traverse.id
)
SELECT id FROM traverse
GROUP BY id
ORDER BY MAX(depth) DESC, id ASC
'''

DESCENDANT_QUERY = '''
 WITH RECURSIVE traverse(id, depth) AS (
     SELECT first.child_id, 1
         FROM {relationship_table} AS first
         LEFT OUTER JOIN {relationship_table} AS second
         ON first.child_id = second.parent_id
     WHERE first.parent_id = %(id)s
 UNION
     SELECT DISTINCT child_id, traverse.depth + 1
         FROM traverse
         INNER JOIN {relationship_table}
         ON {relationship_table}.parent_id = traverse.id
)
SELECT id FROM traverse
GROUP BY id
ORDER BY MAX(depth), id ASC
'''


def filter_order(queryset, field_names, values):
    """Filter queryset where field_name in values, order results in the same order as values."""
    if not isinstance(field_names, list):
        field_names = [field_names]
    case = []
    for pos, value in enumerate(values):
        when_condition = {field_names[0]: value, 'then': pos}
        case.append(When(**when_condition))
    order_by = Case(*case)
    filter_condition = {field_name + '__in': values for field_name in field_names}
    return queryset.filter(**filter_condition).order_by(order_by)


class Node(AbstractModel, ExtendedModel):
    """
    A node in a directed acyclic graph.

    Rather than inheriting directly from this abstract model, use `node_factory`,
    which returns a model inheriting from this model.
    """

    edge_model: type[ExtendedModel]
    parents: 'QuerySet[Node]'

    class Meta:
        abstract = True

    @property
    @abstractmethod
    def children(self) -> models.ManyToManyField:
        """Require `children` to be implemented, as by `node_factory`."""

    @property
    def edge_model_table(self) -> str:
        return self.edge_model._meta.db_table

    def add_child(self, descendant, **kwargs):
        kwargs.update({'parent': self, 'child': descendant})
        cls = self.children.through(**kwargs)
        return cls.save(moderate=False)  # TODO

    def remove_child(self, descendant):
        self.children.through.objects.get(parent=self, child=descendant).delete()

    def add_parent(self, parent, *args, **kwargs):
        return parent.add_child(self, **kwargs)

    def remove_parent(self, parent):
        parent.children.through.objects.get(parent=parent, child=self).delete()

    def filter_order_ids(self, ids):
        return filter_order(self.__class__.objects, 'pk', ids)

    @property
    def ancestor_ids(self) -> list[int]:
        """Return a list of the ids of the node's ancestors."""
        with connection.cursor() as cursor:
            cursor.execute(
                ANCESTOR_QUERY.format(relationship_table=self.edge_model_table),
                {'id': self.id},
            )
            return [row[0] for row in cursor.fetchall()]

    @property
    def ancestor_and_self_ids(self):
        return self.ancestor_ids + [self.id]

    @property
    def self_and_ancestor_ids(self):
        return self.ancestor_and_self_ids[::-1]

    @property
    def ancestors(self):
        return self.filter_order_ids(self.ancestor_ids)

    @property
    def ancestors_and_self(self):
        return self.filter_order_ids(self.self_and_ancestor_ids)

    @property
    def self_and_ancestors(self):
        return self.ancestors_and_self[::-1]

    @property
    def descendant_ids(self):
        with connection.cursor() as cursor:
            cursor.execute(
                DESCENDANT_QUERY.format(relationship_table=self.edge_model_table),
                {'id': self.id},
            )
            return [row[0] for row in cursor.fetchall()]

    @property
    def self_and_descendant_ids(self):
        return [self.id] + self.descendant_ids

    @property
    def descendants_and_self_ids(self):
        return self.self_and_descendant_ids[::-1]

    @property
    def descendants(self):
        return self.filter_order_ids(self.descendant_ids)

    @property
    def self_and_descendants(self):
        return self.filter_order_ids(self.self_and_descendant_ids)

    @property
    def descendants_and_self(self):
        return self.self_and_descendants[::-1]

    @property
    def clan_ids(self):
        return self.ancestor_ids + self.self_and_descendant_ids

    @property
    def clan(self):
        return self.filter_order_ids(self.clan_ids)


def node_factory(
    edge_model: type[ExtendedModel],
    children_null: bool = True,
) -> type[Node]:
    """Return a model class that inherits from `DagNode` and implements `children`."""
    edge_model_table = edge_model._meta.db_table

    class _Node(Node):
        children = models.ManyToManyField(
            'self',
            blank=children_null,
            symmetrical=False,
            through=edge_model,
            related_name='parents',
        )

        class Meta:
            abstract = True

        @property
        def ancestor_ids(self):
            with connection.cursor() as cursor:
                cursor.execute(
                    ANCESTOR_QUERY.format(relationship_table=edge_model_table),
                    {'id': self.id},
                )
                return [row[0] for row in cursor.fetchall()]

        @property
        def descendant_ids(self):
            with connection.cursor() as cursor:
                cursor.execute(
                    DESCENDANT_QUERY.format(relationship_table=edge_model_table),
                    {'id': self.id},
                )
                return [row[0] for row in cursor.fetchall()]

    return _Node


class EdgeManager(models.Manager):
    def descendants(self, node):
        return filter_order(self.model.objects, 'parent_id', node.self_and_descendant_ids)

    def ancestors(self, node):
        return filter_order(self.model.objects, 'child_id', node.self_and_ancestor_ids)

    def clan(self, node):
        return filter_order(self.model.objects, ['parent_id', 'child_id'], node.clan_ids)


class Edge(AbstractModel, Relation):
    """An edge, or relation, in a directed acyclic graph."""

    @property
    @abstractmethod
    def parent(self) -> models.ForeignKey:
        """Require `parent` to be implemented, as by `edge_factory`."""

    @property
    @abstractmethod
    def child(self) -> models.ForeignKey:
        """Require `child` to be implemented, as by `edge_factory`."""

    objects = EdgeManager()

    class Meta:
        abstract = True

    def pre_save(self):
        super().pre_save()
        # Avoid circular ancestry.
        if self.child.id in self.parent.self_and_ancestor_ids:
            raise ValidationError('The child topic is an ancestor of the parent topic.')


def edge_factory(
    node_model: Union[str, type[Node]], bases: Optional[tuple[type[Model]]] = None
) -> type[Edge]:
    """Return a model inheriting from `Edge` and implementing `parent` and `child`."""
    bases = bases or tuple()
    if isinstance(node_model, str):
        try:
            node_model_name = node_model.split('.')[1]
        except IndexError:
            node_model_name = node_model
    else:
        node_model_name = node_model._meta.model_name

    class _Edge(Edge, *bases):
        parent = models.ForeignKey(
            node_model,
            related_name='child_edges',
            on_delete=models.CASCADE,
            verbose_name=f'parent {node_model_name}',
        )
        child = models.ForeignKey(
            node_model,
            related_name=f'parent_edges',
            on_delete=models.CASCADE,
            verbose_name=f'child {node_model_name}',
        )

        class Meta:
            abstract = True

        def pre_save(self):
            super().pre_save()
            for base in bases:
                if issubclass(base, ExtendedModel):
                    super_self: ExtendedModel = super(base, self)
                    super_self.pre_save()

        def post_save(self):
            super().post_save()
            for base in bases:
                if issubclass(base, ExtendedModel):
                    super_self: ExtendedModel = super(base, self)
                    super_self.post_save()

    return _Edge
