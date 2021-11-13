import pytest

from apps.topics.models.topic import Topic

pytestmark = pytest.mark.django_db


def create_topic(**kwargs) -> Topic:
    topic = Topic(**kwargs)
    topic.verified = True
    topic.save(moderate=False)
    return topic


def test_create_topic():
    """Test creating a topic."""
    topic = Topic(name='Foo')
    topic.save(moderate=False)
    assert topic.id > 0
    assert topic.name == 'Foo'


def test_children():
    """Test accessing a topic's direct children."""
    top: Topic = create_topic(name='Top')
    science = create_topic(name='Science')
    science.add_parent(top)
    assert isinstance(science, Topic)
    assert top in science.parents.all()
    sport = create_topic(name='Sport')
    sport.add_parent(top)
    news = create_topic(name='News')
    news.add_parent(top)
    politics = create_topic(name='Politics')
    politics.add_parent(news)
    children = top.children.all()
    assert children.exists(), f'{top} has no children: {type(children)}: {children}'
    assert list(children.order_by('name')) == [news, science, sport]


def test_descendants():
    """Test accessing a topic's descendants."""
    top = create_topic(name='Top')
    science = create_topic(name='Science')
    science.add_parent(top)
    maths = create_topic(name='Maths')
    maths.add_parent(science)
    assert list(top.self_and_descendants.values_list('name', flat=True).order_by('name')) == [
        'Maths',
        'Science',
        'Top',
    ]
    biology = create_topic(name='Biology')
    biology.add_parent(science)
    genetics = create_topic(name='Genetics')
    genetics.add_parent(biology)
    neuroscience = create_topic(name='Neuroscience')
    neuroscience.add_parent(biology)
    assert list(biology.descendants.values_list('name', flat=True).order_by('name')) == [
        'Genetics',
        'Neuroscience',
    ]
    sport = create_topic(name='Sport')
    sport.add_parent(top)
    rugby = create_topic(name='Rugby')
    rugby.add_parent(sport)
    football = create_topic(name='Football')
    football.add_parent(sport)
    champions_league = create_topic(name='Champions League')
    champions_league.add_parent(football)
    world_cup = create_topic(name='World Cup')
    world_cup.add_parent(football)
    assert list(top.self_and_descendants.values_list('name', flat=True).order_by('name')) == [
        'Biology',
        'Champions League',
        'Football',
        'Genetics',
        'Maths',
        'Neuroscience',
        'Rugby',
        'Science',
        'Sport',
        'Top',
        'World Cup',
    ]


# def test_ancestors():
#     """Test accessing a topic's ancestors."""
#     top = create_topic(name='Top')
#     create_topic(name='Sport', parent=top)
#     science = create_topic(name='Science', parent=top)
#     create_topic(name='Maths', parent=science)
#     biology = create_topic(name='Biology', parent=science)
#     genetics = create_topic(name='Genetics', parent=biology)
#     neuroscience = create_topic(name='Neuroscience', parent=biology)
#     neuroscience.refresh_from_db()

#     # Test the `ancestor` custom lookup.
#     actual_ancestors, expected_ancestors = list(
#         Topic.objects.filter(path__ancestor=science.path)
#         .values_list('path', flat=True)
#         .order_by('path')
#     ), [
#         'top.science',
#         'top.science.biology',
#         'top.science.biology.genetics',
#         'top.science.biology.neuroscience',
#         'top.science.maths',
#     ]
#     assert (
#         actual_ancestors == expected_ancestors
#     ), f'{actual_ancestors} != {expected_ancestors}'

#     # Test the `ancestors` property.
#     actual_ancestors, expected_ancestors = (
#         sorted([ancestor.path for ancestor in genetics.ancestors]),
#         sorted([top.path, science.path, biology.path]),
#     )
#     assert (
#         actual_ancestors == expected_ancestors
#     ), f'{actual_ancestors} != {expected_ancestors}'


# def test_simple_recursion():
#     """Test trying to add a relationship that would directly result in a recursion."""
#     foo = create_topic(name='Foo')

#     # we cannot be our own parent...
#     foo.parent = foo
#     with pytest.raises((IntegrityError, ValidationError)):
#         foo.save()


# def test_nested_recursion():
#     """Test trying to add a relationship that would indirectly result in a recursion."""
#     foo = create_topic(name='Foo')
#     bar = create_topic(name='Bar', parent=foo)
#     baz = create_topic(name='Baz', parent=bar)

#     # we cannot be the descendant of one of our parent
#     foo.parent = baz
#     with pytest.raises((IntegrityError, ValidationError)):
#         foo.save()


def test_title():
    """Verify the title is set correctly."""
    foo = create_topic(name='Foo')
    assert foo.title == foo.name
    manually_set_title = 'Manually set title'
    bar = create_topic(name='Bar', title=manually_set_title)
    assert bar.title == manually_set_title
