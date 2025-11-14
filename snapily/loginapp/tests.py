from django.test import TestCase
from .models import *
from django.urls import path
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your tests here.

# testing of models and their fields

class AlbumModelTest(TestCase):

    def setUp(self):
        self.user = CustemUser.objects.create_user(username='testuser', password='12345')
        self.album = Album.objects.create(
            name='Test Album',
            cover_photo='path/to/cover.jpg',
            description='This is a test album.',
            created_by=self.user
        )

    def test_album_creation(self):
        self.assertEqual(self.album.name, 'Test Album')
        self.assertEqual(self.album.created_by.username, 'testuser')
        self.assertFalse(self.album.share_family)

def AlbumPhotoTest(TestCase):

    def setUp(self):
        self.album = Album.objects.create(
            name='Test Album',
            cover_photo='path/to/cover.jpg',
            description='This is a test album.')
    
    def test_photo_upload(self):
        self.assertEqual(str(self.image), 'path/to/photo.jpg')
        self.assertEqual(self.caption, 'A beautiful memory')
        self.assertEqual(self.upload_at.strftime('%Y-%m-%d'), '2024-01-01')


def MemoryModelTest(TestCase):

    def setUp(self):
        self.user = CustemUser.objects.create_user(username='memoryuser', password='12345')
        self.memory = Memory.objects.create(
            title='Test Memory',
            description='This is a test memory.',
            photo='path/to/memory.jpg',
            created_by=self.user
        )

    def test_memory_creation(self):
        self.assertEqual(self.memory.title, 'Test Memory')
        self.assertEqual(self.memory.created_by.username, 'memoryuser')
        self.assertEqual(self.memory.location, 'Prayagraj')
        self.assertEqual(self.memory.tag, 'Holiday')
        self.assertIsNotNone(self.memory.date)
        self.assertIsNotNone(self.memory.time)
        self.assertIsNotNone(self.memory.created_at)
        return f"Memory by {self.user.username} on {self.date} at {self.location}"

def CustemUserModelTest(TestCase):

    def setUp(self):
        self.user = CustemUser.objects.create_user(
            username='customuser',
            password='12345',
            is_family_head = True,
            gender = 'Male',
            relationship_to_admin = 'Self',
            admin_code = 'ADMIN123',
            dob= '1990-01-01',
        )

    def test_custom_user_creation(self):
        self.assertEqual(self.user.username, 'customuser')
        self.assertTrue(self.user.is_family_head)
        self.assertEqual(self.user.gender, 'Male')
        self.assertEqual(self.user.relationship_to_admin, 'Brother')
        self.assertEqual(self.user.admin_code, 'ADMIN123')
        self.assertEqual(self.user.dob.strftime('%Y-%m-%d'), '1990-01-01')
        self.assertIsNone(self.user.profile_pic)

        return f"User: {self.username}, Head: {self.is_family_head}, Member: {self.admin_code}"   

# testing of views 

class GuestUserViewTest(TestCase):
    def test_guestuser_view(self):
        response = self.client.get(reverse('guestuser'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guestuser.html')

class IndexViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
    def test_index_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('index'), follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')