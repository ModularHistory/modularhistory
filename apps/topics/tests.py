import pytest
from django.db import IntegrityError

from apps.topics.models.topic import Topic

pytestmark = pytest.mark.django_db


def create_topic(**kwargs) -> Topic:
    kwargs['verified'] = True
    return Topic.objects.create(**kwargs)


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
    top: Topic = create_topic(name='Top')
    science = create_topic(name='Science', parent=top)
    assert isinstance(science, Topic)
    assert science.parent == top
    sport = create_topic(name='Sport', parent=top)
    news = create_topic(name='News', parent=top)
    create_topic(name='Politics', parent=news)
    direct_children = top.children.all()
    assert (
        direct_children.exists()
    ), f'{top} has no children: {type(direct_children)}: {direct_children}'
    assert list(direct_children.order_by('key')) == [news, science, sport]


def test_descendants():
    """Test accessing a topic's descendants."""
    top = create_topic(name='Top')
    science = create_topic(name='Science', parent=top)
    create_topic(name='Maths', parent=science)
    biology = create_topic(name='Biology', parent=science)
    create_topic(name='Genetics', parent=biology)
    create_topic(name='Neuroscience', parent=biology)

    sport = create_topic(name='Sport', parent=top)
    create_topic(name='Rugby', parent=sport)
    football = create_topic(name='Football', parent=sport)
    create_topic(name='Champions League', parent=football)
    create_topic(name='World Cup', parent=football)
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
    top = create_topic(name='Top', key='top')
    create_topic(name='Sport', key='sport', parent=top)
    science = create_topic(name='Science', key='science', parent=top)
    create_topic(name='Maths', key='maths', parent=science)
    biology = create_topic(name='Biology', key='biology', parent=science)
    genetics = create_topic(name='Genetics', key='genetics', parent=biology)
    neuroscience = create_topic(name='Neuroscience', key='neuroscience', parent=biology)
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
    top = create_topic(name='Top')
    create_topic(name='Sport', parent=top)
    science = create_topic(name='Science', parent=top)
    assert science.path == 'top.science'
    biology = create_topic(name='Biology', parent=science)
    create_topic(name='Genetics', parent=biology)
    create_topic(name='Neuroscience', parent=biology)
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
    top = create_topic(name='Top', key='top')
    create_topic(name='Sport', key='sport', parent=top)
    science = create_topic(name='Science', key='science', parent=top)
    biology = create_topic(name='Biology', key='biology', parent=science)
    create_topic(name='Genetics', key='genetics', parent=biology)
    create_topic(name='Neuroscience', key='neuroscience', parent=biology)

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
    foo = create_topic(name='Foo')

    # we cannot be our own parent...
    foo.parent = foo
    with pytest.raises(IntegrityError):
        foo.save()


def test_nested_recursion():
    """Test trying to add a relationship that would indirectly result in a recursion."""
    foo = create_topic(name='Foo')
    bar = create_topic(name='Bar', parent=foo)
    baz = create_topic(name='Baz', parent=bar)

    # we cannot be the descendant of one of our parent
    foo.parent = baz
    with pytest.raises(IntegrityError):
        foo.save()


def test_title():
    """Verify the title is set correctly."""
    foo = create_topic(name='Foo')
    assert foo.title == foo.name
    manually_set_title = 'Manually set title'
    bar = create_topic(name='Bar', title=manually_set_title)
    assert bar.title == manually_set_title
