from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, Group

User = get_user_model()


class PostUrlTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Testuser')
        cls.user1 = User.objects.create_user(username='UserWithNoRightToEdit')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            slug='testgroup'
        )
        cls.index = reverse('posts:index')
        cls.group_list = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group.slug}
        )
        cls.profile = reverse(
            'posts:profile',
            kwargs={'username': cls.user}
        )
        cls.post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.pk}
        )
        cls.post_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.pk}
        )
        cls.post_create = reverse('posts:post_create')
        cls.post_comment = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.pk}
        )
        cls.unexisting_page = '/unexisting_page/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # The following user1 is used to check if he can access user's funct
        self.authorized_client_noedit = Client()
        self.authorized_client_noedit.force_login(self.user1)
        cache.clear()

    def test_some_urls_exist_at_desired_location_for_unauth_user(self):
        """Check if page returns correct status code when you are NOT
         logged in.
        """
        url_location_names = (
            self.index,
            self.group_list,
            self.profile,
            self.post_detail,
        )
        for url in url_location_names:
            with self.subTest(problem=url):
                request = self.guest_client.get(url)
                self.assertEqual(request.status_code, HTTPStatus.OK)

    def test_unexisting_page_returns_404(self):
        """Check if unexisting page returns 404."""
        request = self.guest_client.get(self.unexisting_page)
        self.assertEqual(request.status_code, HTTPStatus.NOT_FOUND)

    def test_some_urls_exist_at_desided_location_from_auth_user(self):
        """Check if page returns correct status code when you are
         logged in.
        """
        url_location_names = (
            self.index,
            self.group_list,
            self.profile,
            self.post_detail
        )
        for url in url_location_names:
            with self.subTest(problem=url):
                request = self.authorized_client.get(url)
                self.assertEqual(request.status_code, HTTPStatus.OK)

    def test_only_author_can_edit_his_post(self):
        """Check if user is redirected when he wants to edit other's
         user post.
        """
        request = self.authorized_client_noedit.get(self.post_edit)
        self.assertEqual(request.status_code, HTTPStatus.FOUND)

    def test_unauth_user_is_redirected_to_login(self):
        """Check if unauthorized user is redirected to login form
        when he wants to create/edit post.
        """
        url_location_names = (
            self.post_create,
            self.post_edit,
            self.post_comment
        )
        for url in url_location_names:
            with self.subTest(problem=url):
                login = reverse('users:login')
                redirect_url = f'{login}?next={url}'
                request = self.guest_client.get(url, follow=True)
                self.assertRedirects(request, redirect_url)

    def test_auth_user_is_unable_to_edit_someoneelses_post(self):
        """Check user is redirected back to post when he has no right
         to edit post.
        """
        request = self.authorized_client_noedit.get(
            self.post_edit,
            follow=True
        )
        self.assertRedirects(request, self.post_detail)

    def test_urls_use_correct_templates(self):
        """Check if urls use correct templates."""
        template_location_names = (
            (self.index, 'posts/index.html'),
            (self.group_list, 'posts/group_list.html'),
            (self.profile, 'posts/profile.html'),
            (self.post_detail, 'posts/post_detail.html'),
            (self.post_create, 'posts/create_post.html'),
            (self.post_edit, 'posts/create_post.html'),
            (self.unexisting_page, 'core/404.html')
        )
        for url, template in template_location_names:
            with self.subTest(problem=url):
                request = self.authorized_client.get(url)
                self.assertTemplateUsed(request, template)
