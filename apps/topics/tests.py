import pytest
from django.db import IntegrityError

from apps.topics.models.topic import Topic

pytestmark = pytest.mark.django_db


def test_create_topic():
    """Test creating a topic."""
    topic = Topic(name='Foo')
    topic.save()
    assert topic.id > 0
    assert topic.name == 'Foo'
    assert topic.key == 'foo'
    assert topic.path == 'foo'


def test_direct_children():
    """Test accessing a topic's direct children."""
    top = Topic.objects.create(name='Top')
    science = Topic.objects.create(name='Science', parent=top)
    sport = Topic.objects.create(name='Sport', parent=top)
    news = Topic.objects.create(name='News', parent=top)
    Topic.objects.create(name='Politics', parent=news)
    assert list(top.children.order_by('key')) == [news, science, sport]


def test_descendants():
    """Test accessing a topic's descendants."""
    top = Topic.objects.create(name='Top')
    science = Topic.objects.create(name='Science', parent=top)
    Topic.objects.create(name='Maths', parent=science)
    biology = Topic.objects.create(name='Biology', parent=science)
    Topic.objects.create(name='Genetics', parent=biology)
    Topic.objects.create(name='Neuroscience', parent=biology)

    sport = Topic.objects.create(name='Sport', parent=top)
    Topic.objects.create(name='Rugby', parent=sport)
    football = Topic.objects.create(name='Football', parent=sport)
    Topic.objects.create(name='Champions League', parent=football)
    Topic.objects.create(name='World Cup', parent=football)
    assert list(
        Topic.objects.filter(path__ancestor=top.path)
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
    """Test accessing a topic's ancestors."""
    top = Topic.objects.create(name='Top', key='top')
    Topic.objects.create(name='Sport', key='sport', parent=top)
    science = Topic.objects.create(name='Science', key='science', parent=top)
    Topic.objects.create(name='Maths', key='maths', parent=science)
    biology = Topic.objects.create(name='Biology', key='biology', parent=science)
    genetics = Topic.objects.create(name='Genetics', key='genetics', parent=biology)
    neuroscience = Topic.objects.create(
        name='Neuroscience', key='neuroscience', parent=biology
    )
    neuroscience.refresh_from_db()

    # Test the `ancestor` custom lookup.
    actual_ancestors, expected_ancestors = list(
        Topic.objects.filter(path__ancestor=science.path)
        .values_list('path', flat=True)
        .order_by('path')
    ), [
        'top.science',
        'top.science.biology',
        'top.science.biology.genetics',
        'top.science.biology.neuroscience',
        'top.science.maths',
    ]
    assert (
        actual_ancestors == expected_ancestors
    ), f'{actual_ancestors} != {expected_ancestors}'

    # Test the `ancestors` property.
    actual_ancestors, expected_ancestors = (
        sorted([ancestor.path for ancestor in genetics.ancestors]),
        sorted([top.path, science.path, biology.path]),
    )
    assert (
        actual_ancestors == expected_ancestors
    ), f'{actual_ancestors} != {expected_ancestors}'


def test_update_key():
    """Test updating a topic's key."""
    top = Topic.objects.create(name='Top')
    Topic.objects.create(name='Sport', parent=top)
    science = Topic.objects.create(name='Science', parent=top)
    assert science.path == 'top.science'
    biology = Topic.objects.create(name='Biology', parent=science)
    Topic.objects.create(name='Genetics', parent=biology)
    Topic.objects.create(name='Neuroscience', parent=biology)
    assert science.path == 'top.science'
    assert science.descendants.exists()

    # Update the name of a topic.
    # This should result in the key and path of the topic being updated,
    # which should in turn result in the topic's descendants' paths being updated.
    science.name = 'Magic'
    science.save()
    assert list(
        Topic.objects.filter(path__ancestor=top.path)
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
    """Test updating a topic's parent."""
    top = Topic.objects.create(name='Top', key='top')
    Topic.objects.create(name='Sport', key='sport', parent=top)
    science = Topic.objects.create(name='Science', key='science', parent=top)
    biology = Topic.objects.create(name='Biology', key='biology', parent=science)
    Topic.objects.create(name='Genetics', key='genetics', parent=biology)
    Topic.objects.create(name='Neuroscience', key='neuroscience', parent=biology)

    # Change a topic's parent.
    # This should update the topic's path as well as its descendants' paths.
    biology.parent = top
    biology.save()
    assert list(
        Topic.objects.filter(path__ancestor=top.path)
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
    """Test trying to add a relationship that would directly result in a recursion."""
    foo = Topic.objects.create(name='Foo')

    # we cannot be our own parent...
    foo.parent = foo
    with pytest.raises(IntegrityError):
        foo.save()


def test_nested_recursion():
    """Test trying to add a relationship that would indirectly result in a recursion."""
    foo = Topic.objects.create(name='Foo')
    bar = Topic.objects.create(name='Bar', parent=foo)
    baz = Topic.objects.create(name='Baz', parent=bar)

    # we cannot be the descendant of one of our parent
    foo.parent = baz
    with pytest.raises(IntegrityError):
        foo.save()
