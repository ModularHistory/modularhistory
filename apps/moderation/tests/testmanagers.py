# from django.contrib.auth.models import User
# from django.db.models.manager import Manager
# from django.test.testcases import TestCase
# from tests.models import ModelWithSlugField2, ModelWithVisibilityField, UserProfile
# from tests.utils import setup_moderation, teardown_moderation

# from apps.moderation.models import Change
# from apps.moderation.models.moderated_model.manager import ModeratedModelManager
# from apps.moderation.moderator import GenericModerator


# class ModeratedModelManagerManagerTestCase(TestCase):
#     fixtures = ['test_users.json', 'test_moderation.json']

#     def setUp(self):

#         self.user = User.objects.get(username='moderator')
#         self.profile = UserProfile.objects.get(user__username='moderator')

#         class UserProfileModerator(GenericModerator):
#             visibility_column = 'is_public'

#         self.moderation = setup_moderation(
#             [UserProfile, (ModelWithVisibilityField, UserProfileModerator)]
#         )

#     def tearDown(self):
#         teardown_moderation()

#     def test_moderation_objects_manager(self):
#         ManagerClass = ModeratedModelManager()(Manager)

#         self.assertEqual(
#             str(ManagerClass.__bases__),
#             "(<class 'moderation.managers.ModeratedModelManager'>"
#             ", <class 'django.db.models.manager.Manager'>)",
#         )

#     def test_filter_moderations_returns_empty_queryset(self):
#         """Test filter_moderations returns empty queryset
#         for object that has moderated object"""

#         ManagerClass = ModeratedModelManager()(Manager)
#         manager = ManagerClass()
#         manager.model = UserProfile

#         query_set = UserProfile._default_manager.all()
#         moderation = Change(content_object=self.profile)
#         moderation.save()

#         self.assertEqual(str(list(manager.filter_moderations(query_set))), '[]')

#     def test_filter_moderations_returns_object(self):
#         """Test if filter_moderations return object when object
#         doesn't have moderated object or deserialized object is <> object"""
#         moderation = Change(content_object=self.profile)
#         moderation.save()
#         moderation.approve()

#         self.profile.description = 'New'
#         self.profile.save()

#         self.assertEqual(
#             str(list(UserProfile.objects.all())),
#             '[<UserProfile: moderator - http://www.google.com>]',
#         )

#     def test_exclude_objs_by_visibility_col(self):
#         ManagerClass = ModeratedModelManager()(Manager)
#         manager = ManagerClass()
#         manager.model = ModelWithVisibilityField

#         ModelWithVisibilityField(test='test 1').save()
#         ModelWithVisibilityField(test='test 2', is_public=True).save()

#         query_set = ModelWithVisibilityField.objects.all()

#         query_set = manager.exclude_objs_by_visibility_col(query_set)

#         self.assertEqual(
#             str(list(query_set)), '[<ModelWithVisibilityField: test 2 - is public True>]'
#         )
