from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Check if __str__ returns correct name of Model."""
        post = PostModelTest.post
        expected_name = post.text[:15]
        self.assertEqual(expected_name, str(post))
        group = PostModelTest.group
        expected_name = group.title
        self.assertEqual(expected_name, self.group.title)
