import pytest
from django.db import IntegrityError

from apps.topics.models import Topic

pytestmark = pytest.mark.django_db


def test_create_category():
    category = Topic.objects.create(name='Foo', key='bar')
    # Do a full refresh to get the value of the path.
    category.refresh_from_db()
    assert category.id > 0
    assert category.name == 'Foo'
    assert category.key == 'bar'
    assert category.path == 'bar'


def test_direct_children():
    top = Topic.objects.create(key='top')
    science = Topic.objects.create(key='science', parent=top)
    sport = Topic.objects.create(key='sport', parent=top)
    news = Topic.objects.create(key='news', parent=top)
    Topic.objects.create(key='politics', parent=news)
    assert list(top.children.order_by('key')) == [news, science, sport]


def test_descendants():
    top = Topic.objects.create(key='top')
    top.refresh_from_db()

    science = Topic.objects.create(key='science', parent=top)
    Topic.objects.create(key='maths', parent=science)
    biology = Topic.objects.create(key='biology', parent=science)
    Topic.objects.create(key='genetics', parent=biology)
    Topic.objects.create(key='neuroscience', parent=biology)

    sport = Topic.objects.create(key='sport', parent=top)
    Topic.objects.create(key='rugby', parent=sport)
    football = Topic.objects.create(key='football', parent=sport)
    Topic.objects.create(key='champions_league', parent=football)
    Topic.objects.create(key='world_cup', parent=football)

    # we can get all the ancestors of a category (including itself)
    assert list(
        Topic.objects.filter(path__descendant=top.path)
        .values_list('path', flat=True)
        .order_by('path')
    ) == [
        'top',
        'top.science',
        'top.science.biology',
        'top.science.biology.genetics',
        'top.science.biology.neuroscience',
        'top.science.maths',
        'top.sport',
        'top.sport.football',
        'top.sport.football.champions_league',
        'top.sport.football.world_cup',
        'top.sport.rugby',
    ]


def test_ancestors():
    top = Topic.objects.create(key='top')
    top.refresh_from_db()

    Topic.objects.create(key='sport', parent=top)
    science = Topic.objects.create(key='science', parent=top)
    Topic.objects.create(key='maths', parent=science)
    biology = Topic.objects.create(key='biology', parent=science)
    Topic.objects.create(key='genetics', parent=biology)
    neuroscience = Topic.objects.create(key='neuroscience', parent=biology)
    neuroscience.refresh_from_db()

    # we can get all the ancestors of a category (including itself)
    assert list(
        Topic.objects.filter(path__ancestor=neuroscience.path)
        .values_list('path', flat=True)
        .order_by('path')
    ) == [
        'top',
        'top.science',
        'top.science.biology',
        'top.science.biology.neuroscience',
    ]


def test_update_key():
    top = Topic.objects.create(key='top')
    top.refresh_from_db()

    Topic.objects.create(key='sport', parent=top)
    science = Topic.objects.create(key='science', parent=top)
    biology = Topic.objects.create(key='biology', parent=science)
    Topic.objects.create(key='genetics', parent=biology)
    Topic.objects.create(key='neuroscience', parent=biology)

    # update the key of a category, it should update its path as well as
    # the path of all of its descendants
    science.key = 'magic'
    science.save()

    assert list(
        Topic.objects.filter(path__descendant=top.path)
        .values_list('path', flat=True)
        .order_by('path')
    ) == [
        'top',
        'top.magic',
        'top.magic.biology',
        'top.magic.biology.genetics',
        'top.magic.biology.neuroscience',
        'top.sport',
    ]


def test_update_parent():
    top = Topic.objects.create(key='top')
    top.refresh_from_db()

    Topic.objects.create(key='sport', parent=top)
    science = Topic.objects.create(key='science', parent=top)
    biology = Topic.objects.create(key='biology', parent=science)
    Topic.objects.create(key='genetics', parent=biology)
    Topic.objects.create(key='neuroscience', parent=biology)

    # update the parent of a category, it should update its path as well as
    # the path of all of its descendants
    biology.parent = top
    biology.save()

    assert list(
        Topic.objects.filter(path__descendant=top.path)
        .values_list('path', flat=True)
        .order_by('path')
    ) == [
        'top',
        'top.biology',
        'top.biology.genetics',
        'top.biology.neuroscience',
        'top.science',
        'top.sport',
    ]


def test_simple_recursion():
    foo = Topic.objects.create(key='foo')

    # we cannot be our own parent...
    foo.parent = foo
    with pytest.raises(IntegrityError):
        foo.save()


def test_nested_recursion():
    foo = Topic.objects.create(key='foo')
    bar = Topic.objects.create(key='bar', parent=foo)
    baz = Topic.objects.create(key='baz', parent=bar)

    # we cannot be the descendant of one of our parent
    foo.parent = baz
    with pytest.raises(IntegrityError):
        foo.save()
