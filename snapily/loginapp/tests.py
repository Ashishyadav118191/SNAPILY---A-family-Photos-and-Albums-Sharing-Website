from django.test import TestCase
from .models import *

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

   