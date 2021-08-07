# from django.contrib.auth.models import Group, User
# from django.test.testcases import TestCase
# from tests.models import ModelWithSlugField2, ProxyProfile, SuperUserProfile, UserProfile
# from tests.utils import setup_moderation, teardown_moderation

# from apps.moderation.constants import ModerationStatus
# from apps.moderation.fields import SerializedObjectField
# from apps.moderation.models import Change
# from apps.moderation.models.moderated_model import ModeratedModelManager
# from apps.moderation.moderator import GenericModerator
# from apps.moderation.register import ModerationManager


# class SerializationTestCase(TestCase):
#     fixtures = ['test_users.json', 'test_moderation.json']

#     def setUp(self):
#         self.user = User.objects.get(username='moderator')
#         self.profile = UserProfile.objects.get(user__username='moderator')

#     def test_serialize_of_object(self):
#         """Test if object is properly serialized to json"""

#         json_field = SerializedObjectField()

#         serialized_str = json_field._serialize(self.profile)

#         self.assertIn('"pk": 1', serialized_str)
#         self.assertIn('"model": "tests.userprofile"', serialized_str)
#         self.assertIn('"fields": {', serialized_str)
#         self.assertIn('"url": "http://www.google.com"', serialized_str)
#         self.assertIn('"user": 1', serialized_str)
#         self.assertIn('"description": "Old description"', serialized_str)

#     def test_serialize_with_inheritance(self):
#         """Test if object is properly serialized to json"""

#         profile = SuperUserProfile(
#             description='Profile for new super user',
#             url='http://www.test.com',
#             user=User.objects.get(username='user1'),
#             super_power='invisibility',
#         )
#         profile.save()
#         json_field = SerializedObjectField()

#         serialized_str = json_field._serialize(profile)

#         self.assertIn('"pk": 2', serialized_str)
#         self.assertIn('"model": "tests.superuserprofile"', serialized_str)
#         self.assertIn('"fields": {"super_power": "invisibility"}', serialized_str)
#         self.assertIn('"pk": 2', serialized_str)
#         self.assertIn('"model": "tests.userprofile"', serialized_str)
#         self.assertIn('"url": "http://www.test.com"', serialized_str)
#         self.assertIn('"user": 2', serialized_str)
#         self.assertIn('"description": "Profile for new super user"', serialized_str)
#         self.assertIn('"fields": {', serialized_str)

#     def test_deserialize(self):
#         value = (
#             '[{"pk": 1, "model": "tests.userprofile", "fields": '
#             '{"url": "http://www.google.com", "user": 1, '
#             '"description": "Profile description"}}]'
#         )
#         json_field = SerializedObjectField()
#         object = json_field._deserialize(value)

#         self.assertEqual(repr(object), '<UserProfile: moderator - http://www.google.com>')
#         self.assertTrue(isinstance(object, UserProfile))

#     def test_deserialize_with_inheritance(self):
#         value = (
#             '[{"pk": 2, "model": "tests.superuserprofile",'
#             ' "fields": {"super_power": "invisibility"}}, '
#             '{"pk": 2, "model": "tests.userprofile", "fields":'
#             ' {"url": "http://www.test.com", "user": 2,'
#             ' "description": "Profile for new super user"}}]'
#         )

#         json_field = SerializedObjectField()
#         object = json_field._deserialize(value)

#         self.assertTrue(isinstance(object, SuperUserProfile))
#         self.assertEqual(
#             repr(object), '<SuperUserProfile: user1 - http://www.test.com - invisibility>'
#         )

#     def test_deserialzed_object(self):
#         moderation = Change(content_object=self.profile)
#         self.profile.description = 'New description'
#         moderation.changed_object = self.profile
#         moderation.save()
#         pk = moderation.pk

#         moderation = Change.objects.get(pk=pk)

#         self.assertEqual(moderation.changed_object.description, 'New description')

#         self.assertEqual(moderation.content_object.description, 'Old description')

#     def test_change_of_deserialzed_object(self):
#         self.profile.description = 'New description'
#         moderation = Change(content_object=self.profile)
#         moderation.save()
#         pk = moderation.pk

#         self.profile.description = 'New changed description'
#         moderation.changed_object = self.profile.description
#         moderation.save()

#         moderation = Change.objects.get(pk=pk)

#         self.assertEqual(moderation.changed_object.description, 'New changed description')

#     def test_serialize_proxy_model(self):
#         'Handle proxy models in the serialization.'
#         profile = ProxyProfile(
#             description="I'm a proxy.",
#             url='http://example.com',
#             user=User.objects.get(username='user1'),
#         )
#         profile.save()
#         json_field = SerializedObjectField()

#         serialized_str = json_field._serialize(profile)

#         self.assertIn('"pk": 2', serialized_str)
#         self.assertIn('"model": "tests.proxyprofile"', serialized_str)
#         self.assertIn('"url": "http://example.com"', serialized_str)
#         self.assertIn('"user": 2', serialized_str)
#         self.assertIn('"description": "I\'m a proxy."', serialized_str)
#         self.assertIn('"fields": {', serialized_str)

#     def test_deserialize_proxy_model(self):
#         'Correctly restore a proxy model.'
#         value = (
#             '[{"pk": 2, "model": "tests.proxyprofile", "fields": '
#             '{"url": "http://example.com", "user": 2, '
#             '"description": "I\'m a proxy."}}]'
#         )

#         json_field = SerializedObjectField()
#         profile = json_field._deserialize(value)
#         self.assertTrue(isinstance(profile, ProxyProfile))
#         self.assertEqual(profile.url, 'http://example.com')
#         self.assertEqual(profile.description, "I\'m a proxy.")
#         self.assertEqual(profile.user_id, 2)


# class ModerateTestCase(TestCase):
#     fixtures = ['test_users.json', 'test_moderation.json']

#     def setUp(self):
#         self.user = User.objects.get(username='moderator')
#         self.profile = UserProfile.objects.get(user__username='moderator')
#         self.moderation = setup_moderation([UserProfile])

#     def tearDown(self):
#         teardown_moderation()

#     def test_objects_with_no_moderation_are_visible(self):
#         """
#         Simulate conditions where moderation is added to a model which
#         already has existing objects, which should remain visible.
#         """

#         Change.objects.all().delete()

#         self.assertEqual(
#             [self.profile],
#             list(self.profile.__class__.objects.all()),
#             'Objects with no attached Moderation should be visible ' 'by default.',
#         )

#     def test_approval_status_pending(self):
#         """test if before object approval status is pending"""

#         self.profile.description = 'New description'
#         self.profile.save()

#         self.assertEqual(self.profile.moderation.status, ModerationStatus.PENDING)

#     def test_moderate(self):
#         self.profile.description = 'New description'
#         self.profile.save()

#         self.profile.moderation._moderate(ModerationStatus.APPROVED, self.user, 'Reason')

#         self.assertEqual(self.profile.moderation.status, ModerationStatus.APPROVED)
#         self.assertEqual(self.profile.moderation.by, self.user)
#         self.assertEqual(self.profile.moderation.reason, 'Reason')

#     def test_multiple_moderations_throws_exception_by_default(self):
#         self.profile.description = 'New description'
#         self.profile.save()

#         moderation = Change.objects.create(content_object=self.profile)
#         moderation.approve(by=self.user)

#         with self.assertRaises(ModeratedModelManager.MultipleModerations):
#             self.profile.__class__.objects.get(id=self.profile.id)

#     def test_approve_new_moderation(self):
#         """
#         When a newly created object is approved, it should become visible
#         in standard querysets.
#         """
#         profile = self.profile.__class__(
#             description='Profile for new user', url='http://www.test.com', user=self.user
#         )

#         profile.save()
#         self.assertEqual(
#             MODERATION_DRAFT_STATE,
#             profile.moderation.state,
#             'Before first approval, the profile should be in draft state, '
#             'to hide it from querysets.',
#         )

#         profile.moderation.approve(self.user)
#         self.assertEqual(
#             MODERATION_READY_STATE,
#             profile.moderation.state,
#             'After first approval, the profile should be in ready state, '
#             'to show it in querysets.',
#         )

#         user_profile = self.profile.__class__.objects.get(url='http://www.test.com')

#         self.assertEqual(user_profile.description, 'Profile for new user')
#         self.assertEqual(
#             [profile],
#             list(self.profile.__class__.objects.filter(pk=profile.pk)),
#             'New profile objects should be visible after being accepted',
#         )

#     def test_reject_new_moderation(self):
#         """
#         When a newly created object is rejected, it should remain invisible
#         in standard querysets.
#         """
#         profile = self.profile.__class__(
#             description='Profile for new user', url='http://www.test.com', user=self.user
#         )

#         profile.save()
#         self.assertEqual(
#             MODERATION_DRAFT_STATE,
#             profile.moderation.state,
#             'Before first approval, the profile should be in draft state, '
#             'to hide it from querysets.',
#         )

#         profile.moderation.reject(self.user)
#         self.assertEqual(
#             MODERATION_DRAFT_STATE,
#             profile.moderation.state,
#             'After rejection, the profile should still be in draft state, '
#             'to hide it from querysets.',
#         )

#         user_profile = self.profile.__class__.unmoderations.get(url='http://www.test.com')
#         self.assertEqual(user_profile.description, 'Profile for new user')
#         self.assertEqual(
#             [],
#             list(self.profile.__class__.objects.filter(pk=profile.pk)),
#             'New profile objects should be hidden after being rejected',
#         )

#     def test_approve_modified_moderation(self):
#         """
#         When a previously approved object is updated and approved, it should
#         remain visible in standard querysets, with the new data saved in the
#         object.
#         """
#         self.profile.description = 'New description'
#         self.profile.save()
#         self.profile.moderation.approve(self.user)

#         self.assertEqual(
#             MODERATION_READY_STATE,
#             self.profile.moderation.state,
#             'After first approval, the profile should be in ready state, '
#             'to show it in querysets.',
#         )

#         user_profile = self.profile.__class__.objects.get(id=self.profile.id)
#         self.assertEqual(user_profile.description, 'New description')
#         self.assertEqual(
#             [self.profile],
#             list(self.profile.__class__.objects.filter(pk=self.profile.pk)),
#             'Modified profile objects should be visible after being accepted',
#         )

#     def test_reject_modified_moderation(self):
#         """
#         When a previously approved object is updated and rejected, it should
#         remain visible in standard querysets, but with the old (previously
#         approved) data saved in the object.
#         """
#         Change.objects.create(content_object=self.profile)
#         self.profile.moderation.approve(self.user)

#         self.profile.description = 'New description'
#         self.profile.save()

#         self.profile.moderation.reject(self.user)
#         self.assertEqual(
#             MODERATION_READY_STATE,
#             self.profile.moderation.state,
#             'After rejection, the profile should still be in ready state, '
#             'to show it in querysets, but with the old data.',
#         )

#         user_profile = self.profile.__class__.objects.get(id=self.profile.id)

#         self.assertEqual(user_profile.description, 'Old description')
#         self.assertEqual(self.profile.moderation.status, ModerationStatus.REJECTED)
#         self.assertEqual(
#             [self.profile],
#             list(self.profile.__class__.objects.filter(pk=self.profile.pk)),
#             'Modified profile objects should still be visible after being '
#             'rejected, but with the old data',
#         )

#         # Test making another change that's rejected, and that the data
#         # saved in the object is still the previously approved data.
#         self.profile.description = 'Another bad description'
#         self.profile.save()

#         self.profile.moderation.reject(self.user)

#         user_profile = self.profile.__class__.objects.get(id=self.profile.id)

#         self.assertEqual(user_profile.description, 'Old description')
#         self.assertEqual(self.profile.moderation.status, ModerationStatus.REJECTED)
#         self.assertEqual(
#             [self.profile],
#             list(self.profile.__class__.objects.filter(pk=self.profile.pk)),
#             'Modified profile objects should still be visible after being '
#             'rejected, but with the old data',
#         )

#     def test_has_object_been_changed_should_be_true(self):
#         self.profile.description = 'Old description'
#         moderation = Change(content_object=self.profile)
#         moderation.save()
#         moderation.approve(by=self.user)

#         user_profile = self.profile.__class__.objects.get(id=self.profile.id)

#         self.profile.description = 'New description'
#         moderation = Change(content_object=self.profile)
#         moderation.save()

#         value = moderation.has_object_been_changed(user_profile)

#         self.assertEqual(value, True)

#     def test_has_object_been_changed_should_be_false(self):
#         moderation = Change(content_object=self.profile)
#         moderation.save()

#         value = moderation.has_object_been_changed(self.profile)

#         self.assertEqual(value, False)


# class AutoModerateTestCase(TestCase):
#     fixtures = ['test_users.json', 'test_moderation.json']

#     def setUp(self):
#         self.moderation = ModerationManager()

#         class UserProfileModerator(GenericModerator):
#             auto_approve_for_superusers = True
#             auto_approve_for_staff = True
#             auto_reject_for_groups = ['banned']

#         self.moderation.register(UserProfile, UserProfileModerator)

#         self.user = User.objects.get(username='moderator')
#         self.profile = UserProfile.objects.get(user__username='moderator')

#     def tearDown(self):
#         teardown_moderation()

#     def test_auto_approve_helper_status_approved(self):
#         self.profile.description = 'New description'
#         self.profile.save()

#         status = self.profile.moderation.automoderate(self.user)
#         self.assertEqual(status, ModerationStatus.APPROVED)

#         profile = UserProfile.objects.get(user__username='moderator')
#         self.assertEqual(profile.description, 'New description')

#     def test_auto_approve_helper_status_rejected(self):
#         group = Group(name='banned')
#         group.save()
#         self.user.groups.add(group)
#         self.user.save()

#         self.profile.description = 'New description'
#         self.profile.save()

#         status = self.profile.moderation.automoderate(self.user)

#         profile = UserProfile.unmoderations.get(user__username='moderator')

#         self.assertEqual(status, ModerationStatus.REJECTED)
#         self.assertEqual(profile.description, 'Old description')

#         teardown_moderation()
