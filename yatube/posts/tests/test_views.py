import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache


from ..forms import PostForm
from ..models import Post, Group, Comment, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
OBJECT_EXISTS = 1
OBJECT_DOESNT_EXIST = 0


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Testuser',
            first_name='Ivan',
            last_name='Ivanov'
        )
        cls.user1 = User.objects.create_user(
            username='UserWithNoRightToEdit'
        )
        #  Creating 2 groups for testing
        cls.group1 = Group.objects.create(
            slug='testgroup',
            title='Группа для теста'
        )
        cls.group2 = Group.objects.create(
            slug='testgroupnew',
            title='Группа для теста номер 2'
        )
        # Creating 15 posts with different groups for testing
        cls.post1 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост1 с id 4',
            group=cls.group1
        )
        for i in range(5, 19):
            Post.objects.create(
                author=cls.user,
                text='Тестовый пост2',
                id=i,
                group=cls.group1
            )
        cls.index = reverse('posts:index')
        cls.group_list = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group1.slug}
        )
        cls.profile = reverse(
            'posts:profile',
            kwargs={'username': cls.user}
        )
        cls.post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post1.pk}
        )
        cls.post_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post1.pk}
        )
        cls.post_create = reverse('posts:post_create')
        cls.post_comment = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post1.pk}
        )
        cls.profile_follow = reverse(
            'posts:profile_follow',
            kwargs={'username': cls.user}
        )
        cls.profile_unfollow = reverse(
            'posts:profile_unfollow',
            kwargs={'username': cls.user}
        )
        cls.follow = reverse('posts:follow_index')

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_noedit = Client()
        self.authorized_client_noedit.force_login(self.user1)
        cache.clear()

    def test_page_use_correct_templates(self):
        """Check if pages use correct templates."""
        templates_pages_names = (
            (self.index, 'posts/index.html'),
            (self.group_list, 'posts/group_list.html'),
            (self.profile, 'posts/profile.html'),
            (self.post_detail, 'posts/post_detail.html'),
            (self.post_create, 'posts/create_post.html'),
            (self.post_edit, 'posts/create_post.html'),
        )
        for reverse_name, template in templates_pages_names:
            with self.subTest(problem=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_post_context_with_pagination(self):
        """
        Check if posts with correct information are displayed
        on the index page with pagination.
        """
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.get_full_name()
        self.assertEqual(post_author_0, self.user.get_full_name())
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(
            response.context.get('title'), 'Последние обновления на сайте'
        )

    def test_group_list_page_context_with_pagination_and_group_filter(self):
        """Check if group list is filled
        with only one group posts with pagination.
        """
        response = self.authorized_client.get(self.group_list)
        for i in range(0, 10):  # Check all the posts belong to same group
            first_object = response.context['page_obj'][i]
            self.assertEqual(first_object.group.title, self.group1.title)
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(
            response.context.get('title'), 'Записи сообщества '
                                           'Группа для теста'
        )

    def test_profile__context_is_filled_with_his_own_posts(self):
        """Check if only user's posts are in his profile."""
        response = self.authorized_client.get(self.profile)
        for i in range(0, 10):  # Check all the posts belong to same user
            first_object = response.context['page_obj'][i]
            self.assertEqual(
                first_object.author.get_full_name(),
                self.user.get_full_name()
            )
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(
            response.context.get('title'), 'Профиль пользователя Ivan Ivanov'
        )
        self.assertEqual(
            response.context.get('author').username, self.user.username
        )
        self.assertEqual(
            response.context.get('total_posts'), 15
        )

    def test_post_detail_context_is_correct(self):
        """Check if post_details shows only one post with correct id."""
        response = self.authorized_client.get(self.post_detail)

        self.assertEqual(
            response.context.get(
                'posts'
            ).author.get_full_name(), self.user.get_full_name()
        )
        self.assertEqual(
            response.context.get('posts').text, self.post1.text
        )
        self.assertEqual(
            response.context.get('posts').group.title, self.group1.title
        )
        self.assertEqual(
            response.context.get('total_posts'), 15
        )
        self.assertEqual(
            response.context.get('title'), 'Пост Тестовый пост1 с id 4'
        )

    def test_post_creation_form_context_is_correct(self):
        """Check if post creation form context is correct."""
        response = self.authorized_client.get(self.post_create)
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.models.ModelChoiceField),
            ('image', forms.fields.ImageField)
        )
        for value in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form')
                self.assertIsInstance(form_field, PostForm)
        self.assertEqual(
            response.context.get('title'), 'Новая запись в блоге.'
        )

    def test_post_edit_form_context_is_correct(self):
        """Check if post edit form context is correct."""
        response = self.authorized_client.get(self.post_edit)
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.models.ModelChoiceField),
        )
        for value in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form')
                self.assertIsInstance(form_field, PostForm)
        self.assertEqual(
            response.context.get('is_edit'), True
        )
        self.assertEqual(
            response.context.get('post'), self.post1
        )
        self.assertEqual(
            response.context.get('title'), 'Редактирование записи'
        )

    def test_post_creation_and_distribution(self):
        """
        Check if after creating post with image it
         belongs where it has to.
        """
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        # Creating a post
        self.post3 = Post.objects.create(
            author=self.user,
            text='Новый пост',
            group=self.group2,
            image=uploaded
        )
        # Check it is on main
        response = self.authorized_client.get(self.index)
        self.assertEqual(
            response.context['page_obj'][0],
            self.post3
        )
        # Check it is in testgroupnew
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group2.slug})
        )
        self.assertEqual(
            response.context['page_obj'][0],
            self.post3
        )
        # Check it is NOT in testgroup
        response = self.authorized_client.get(self.group_list)
        self.assertNotEqual(
            response.context['page_obj'][0],
            self.post3
        )
        # Check it is in users profile
        response = self.authorized_client.get(self.profile)
        self.assertEqual(
            response.context['page_obj'][0],
            self.post3
        )
        # Check it has all the context in post profile
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post3.pk})
        )
        self.assertEqual(
            response.context['posts'],
            self.post3
        )

    def test_comment_created_by_auth_user_is_in_database(self):
        """Check if comment created by auth user is in database."""
        self.comment = Comment.objects.create(
            author=self.user,
            text='Комментарий к посту',
            post=self.post1
        )
        response = self.authorized_client.get(self.post_detail)
        self.assertEqual(response.context['comments'][0], self.comment)

    def test_cache_is_working(self):
        """Check if caching is working."""
        self.post4 = Post.objects.create(
            author=self.user,
            text='Новый пост8888',
            group=self.group2
        )
        #  Getting content before and after post deleted
        response1 = self.authorized_client.get(self.index).content
        self.post4.delete()
        response2 = self.authorized_client.get(self.index).content
        #  Asserting nothing has changed despite deleting post
        self.assertEqual(
            response1,
            response2
        )
        #  Clearing cache
        cache.clear()
        #  Getting new response after cache was cleared
        response2 = self.authorized_client.get(self.index).content
        self.assertNotEqual(
            response1,
            response2
        )

    def test_auth_user_is_able_to_follow_other_users(self):
        """
        Check if auth user is able to follow other users and
         redirected to profile.
        """
        response_follow = self.authorized_client.get(self.profile_follow)
        response_unfollow = self.authorized_client.get(self.profile_unfollow)
        Follow.objects.create(user=self.user, author=self.user)
        self.assertRedirects(response_follow, self.profile)

        result = Follow.objects.all().count()
        self.assertEqual(result, OBJECT_EXISTS)
        self.assertRedirects(response_unfollow, self.profile)
        Follow.objects.filter(user=self.user, author=self.user).delete()
        result = Follow.objects.all().count()
        self.assertEqual(result, OBJECT_DOESNT_EXIST)

    def test_post_is_shown_in_follow_page(self):
        """Check if new post is shown in follow_index."""
        response = self.authorized_client.get(self.follow)
        response2 = self.authorized_client_noedit.get(self.follow)
        Follow.objects.create(user=self.user, author=self.user)
        self.post2 = Post.objects.create(
            author=self.user,
            text='Тестовый пост в подписке',
            group=self.group1
        )
        count = response2.context['posts'].count()
        self.assertEqual(response.context['posts'][0], self.post2)
        self.assertEqual(count, OBJECT_DOESNT_EXIST)
