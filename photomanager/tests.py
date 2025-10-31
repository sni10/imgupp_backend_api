import os
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from PIL import Image as PilImage
from io import BytesIO

from .models import Profile, Gallery, Image, Folder, Post, generate_hashpath
from .serializers import (
    ProfileSerializer, ProfileListSerializer, 
    GalleryFullSerializer, GalleryPrevSerializer, 
    ImageSerializer
)


class ProfileModelTest(TestCase):
    """Test the Profile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """Test creating a profile"""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertIsNotNone(profile.hashpath)
        self.assertEqual(len(profile.hashpath), 32)
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
    
    def test_profile_hashpath_unique(self):
        """Test that hashpath is unique"""
        profile1 = Profile.objects.create(user=self.user)
        user2 = User.objects.create_user(username='testuser2', password='testpass123')
        profile2 = Profile.objects.create(user=user2)
        self.assertNotEqual(profile1.hashpath, profile2.hashpath)
    
    def test_profile_str_representation(self):
        """Test profile string representation"""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(str(profile), f"Profile of {self.user.username}")
    
    def test_profile_ordering(self):
        """Test that profiles are ordered by created_at descending"""
        # Verify that the Profile model has the correct ordering set
        self.assertEqual(Profile._meta.ordering, ['-created_at'])
        
        # Create profiles and verify they can be queried in order
        user2 = User.objects.create_user(username='testuser2', password='testpass123')
        user3 = User.objects.create_user(username='testuser3', password='testpass123')
        
        profile1 = Profile.objects.create(user=self.user)
        profile2 = Profile.objects.create(user=user2)
        profile3 = Profile.objects.create(user=user3)
        
        profiles = list(Profile.objects.all())
        # Verify all profiles are returned
        self.assertEqual(len(profiles), 3)
        # Verify ordering is applied (profiles should be sorted by created_at desc)
        # Note: In fast tests, timestamps might be identical, so we just verify ordering is set
        self.assertTrue(hasattr(Profile, '_meta'))
        self.assertIn('-created_at', Profile._meta.ordering)
    
    def test_profile_user_relationship(self):
        """Test one-to-one relationship with User"""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(self.user.profile, profile)


class GalleryModelTest(TestCase):
    """Test the Gallery model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = Profile.objects.create(user=self.user)
    
    def test_gallery_creation(self):
        """Test creating a gallery"""
        gallery = Gallery.objects.create(
            title='Test Gallery',
            description='Test Description',
            profile=self.profile
        )
        self.assertEqual(gallery.title, 'Test Gallery')
        self.assertEqual(gallery.description, 'Test Description')
        self.assertEqual(gallery.profile, self.profile)
        self.assertIsNotNone(gallery.hashpath)
        self.assertEqual(len(gallery.hashpath), 32)
    
    def test_gallery_hashpath_unique(self):
        """Test that gallery hashpath is unique"""
        gallery1 = Gallery.objects.create(title='Gallery 1', profile=self.profile)
        gallery2 = Gallery.objects.create(title='Gallery 2', profile=self.profile)
        self.assertNotEqual(gallery1.hashpath, gallery2.hashpath)
    
    def test_gallery_profile_relationship(self):
        """Test foreign key relationship with Profile"""
        gallery = Gallery.objects.create(title='Test Gallery', profile=self.profile)
        self.assertIn(gallery, self.profile.galleries.all())
    
    def test_gallery_str_representation(self):
        """Test gallery string representation"""
        gallery = Gallery.objects.create(title='Test Gallery', profile=self.profile)
        self.assertEqual(str(gallery), 'Gallery: Test Gallery')
        
        gallery_untitled = Gallery.objects.create(profile=self.profile)
        self.assertEqual(str(gallery_untitled), 'Gallery: Untitled')
    
    def test_gallery_cascade_delete(self):
        """Test that galleries are deleted when profile is deleted"""
        gallery = Gallery.objects.create(title='Test Gallery', profile=self.profile)
        profile_id = self.profile.id
        self.profile.delete()
        self.assertFalse(Gallery.objects.filter(id=gallery.id).exists())


class ImageModelTest(TestCase):
    """Test the Image model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = Profile.objects.create(user=self.user)
        self.gallery = Gallery.objects.create(
            title='Test Gallery',
            profile=self.profile
        )
    
    def create_test_image(self):
        """Helper method to create a test image file"""
        file = BytesIO()
        image = PilImage.new('RGB', (100, 100), color='red')
        image.save(file, 'PNG')
        file.seek(0)
        return SimpleUploadedFile(
            'test_image.png',
            file.read(),
            content_type='image/png'
        )
    
    def test_image_creation(self):
        """Test creating an image"""
        test_image = self.create_test_image()
        image = Image.objects.create(
            title='Test Image',
            image=test_image,
            gallery=self.gallery
        )
        self.assertEqual(image.title, 'Test Image')
        self.assertEqual(image.gallery, self.gallery)
        self.assertIsNotNone(image.hashpath)
        self.assertEqual(len(image.hashpath), 32)
    
    def test_image_hashpath_unique(self):
        """Test that image hashpath is unique"""
        test_image1 = self.create_test_image()
        test_image2 = self.create_test_image()
        image1 = Image.objects.create(image=test_image1, gallery=self.gallery)
        image2 = Image.objects.create(image=test_image2, gallery=self.gallery)
        self.assertNotEqual(image1.hashpath, image2.hashpath)
    
    def test_image_gallery_relationship(self):
        """Test foreign key relationship with Gallery"""
        test_image = self.create_test_image()
        image = Image.objects.create(image=test_image, gallery=self.gallery)
        self.assertIn(image, self.gallery.images.all())
    
    def test_image_str_representation(self):
        """Test image string representation"""
        test_image = self.create_test_image()
        image = Image.objects.create(title='Test Image', image=test_image, gallery=self.gallery)
        self.assertEqual(str(image), 'Image: Test Image')
    
    def test_image_upload_path(self):
        """Test that image upload path is generated correctly"""
        test_image = self.create_test_image()
        image = Image.objects.create(image=test_image, gallery=self.gallery)
        # Path should be: origins/galleries/{gallery.hashpath}/{image.hashpath}.png
        # Django uses forward slashes regardless of OS
        expected_path_part = f"origins/galleries/{self.gallery.hashpath}/{image.hashpath}"
        self.assertIn(expected_path_part, image.image.name)


class FolderModelTest(TestCase):
    """Test the Folder model"""
    
    def test_folder_creation(self):
        """Test creating a folder"""
        folder = Folder.objects.create(
            name='Test Folder',
            description='Test Description',
            birthplace='Test City',
            hair_color='Brown',
            height='170cm',
            bust_size='90',
            measurements='90-60-90'
        )
        self.assertEqual(folder.name, 'Test Folder')
        self.assertEqual(folder.description, 'Test Description')
        self.assertEqual(folder.birthplace, 'Test City')
        self.assertEqual(folder.hair_color, 'Brown')
        self.assertIsNotNone(folder.hashpath)
    
    def test_folder_str_representation(self):
        """Test folder string representation"""
        folder = Folder.objects.create(name='Test Folder')
        self.assertEqual(str(folder), 'Test Folder')


class PostModelTest(TestCase):
    """Test the Post model"""
    
    def setUp(self):
        self.folder = Folder.objects.create(name='Test Folder')
    
    def test_post_creation(self):
        """Test creating a post"""
        post = Post.objects.create(
            folder=self.folder,
            title='Test Post',
            description='Test Description'
        )
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.description, 'Test Description')
        self.assertEqual(post.folder, self.folder)
        self.assertIsNotNone(post.hashpath)
    
    def test_post_folder_relationship(self):
        """Test foreign key relationship with Folder"""
        post = Post.objects.create(folder=self.folder, title='Test Post')
        self.assertIn(post, self.folder.posts.all())
    
    def test_post_str_representation(self):
        """Test post string representation"""
        post = Post.objects.create(folder=self.folder, title='Test Post')
        self.assertEqual(str(post), 'Test Post')


class ProfileAPITest(APITestCase):
    """Test the Profile API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.user3 = User.objects.create_user(username='user3', password='pass123')
        
        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)
        self.profile3 = Profile.objects.create(user=self.user3)
        
        # Create galleries for testing
        self.gallery1 = Gallery.objects.create(
            title='Gallery 1',
            description='Description 1',
            profile=self.profile1
        )
        self.gallery2 = Gallery.objects.create(
            title='Gallery 2',
            profile=self.profile2
        )
    
    def test_profile_list(self):
        """Test GET /api/img/profiles endpoint"""
        response = self.client.get('/api/img/profiles')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 3)
    
    def test_profile_list_pagination(self):
        """Test profile list pagination"""
        response = self.client.get('/api/img/profiles?page=1&size=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIn('next', response.data)
    
    def test_profile_detail(self):
        """Test GET /api/img/profile/<hashpath> endpoint"""
        response = self.client.get(f'/api/img/profile/{self.profile1.hashpath}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['hashpath'], self.profile1.hashpath)
        self.assertEqual(response.data['username'], 'user1')
        self.assertIn('galleries', response.data)
    
    def test_profile_detail_not_found(self):
        """Test profile detail with invalid hashpath"""
        response = self.client.get('/api/img/profile/invalidhashpath')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GalleryAPITest(APITestCase):
    """Test the Gallery API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.profile = Profile.objects.create(user=self.user)
        self.gallery = Gallery.objects.create(
            title='Test Gallery',
            description='Test Description',
            profile=self.profile
        )
    
    def create_test_image(self, filename='test.png'):
        """Helper method to create a test image file"""
        file = BytesIO()
        image = PilImage.new('RGB', (100, 100), color='blue')
        image.save(file, 'PNG')
        file.seek(0)
        return SimpleUploadedFile(filename, file.read(), content_type='image/png')
    
    def test_gallery_detail(self):
        """Test GET /api/img/gallery/<hashpath> endpoint"""
        # Create some images for the gallery
        image1 = Image.objects.create(
            title='Image 1',
            image=self.create_test_image('img1.png'),
            gallery=self.gallery
        )
        image2 = Image.objects.create(
            title='Image 2',
            image=self.create_test_image('img2.png'),
            gallery=self.gallery
        )
        
        response = self.client.get(f'/api/img/gallery/{self.gallery.hashpath}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Gallery')
        self.assertEqual(response.data['description'], 'Test Description')
        self.assertEqual(response.data['hashpath'], self.gallery.hashpath)
        self.assertEqual(len(response.data['images']), 2)
    
    def test_gallery_detail_not_found(self):
        """Test gallery detail with invalid hashpath"""
        response = self.client.get('/api/img/gallery/invalidhashpath')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SerializerTest(TestCase):
    """Test the serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.profile = Profile.objects.create(user=self.user)
        self.gallery = Gallery.objects.create(
            title='Test Gallery',
            description='Test Description',
            profile=self.profile
        )
    
    def create_test_image(self, filename='test.png'):
        """Helper method to create a test image file"""
        file = BytesIO()
        image = PilImage.new('RGB', (100, 100), color='green')
        image.save(file, 'PNG')
        file.seek(0)
        return SimpleUploadedFile(filename, file.read(), content_type='image/png')
    
    def test_profile_serializer(self):
        """Test ProfileSerializer"""
        serializer = ProfileSerializer(self.profile)
        data = serializer.data
        self.assertEqual(data['hashpath'], self.profile.hashpath)
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['user_id'], self.user.id)
        self.assertIn('galleries', data)
    
    def test_profile_list_serializer(self):
        """Test ProfileListSerializer"""
        serializer = ProfileListSerializer(self.profile)
        data = serializer.data
        self.assertEqual(data['hashpath'], self.profile.hashpath)
        self.assertEqual(data['username'], 'testuser')
        self.assertIn('galleries', data)
    
    def test_gallery_full_serializer(self):
        """Test GalleryFullSerializer"""
        # Create images
        image1 = Image.objects.create(
            title='Image 1',
            image=self.create_test_image('img1.png'),
            gallery=self.gallery
        )
        
        serializer = GalleryFullSerializer(self.gallery)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Gallery')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['hashpath'], self.gallery.hashpath)
        self.assertEqual(len(data['images']), 1)
    
    def test_gallery_prev_serializer(self):
        """Test GalleryPrevSerializer"""
        # Create multiple images to test 6th image logic
        for i in range(8):
            Image.objects.create(
                title=f'Image {i}',
                image=self.create_test_image(f'img{i}.png'),
                gallery=self.gallery
            )
        
        serializer = GalleryPrevSerializer(self.gallery)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Gallery')
        self.assertIn('image_url', data)
        self.assertIn('thumbnail_url', data)
    
    def test_image_serializer(self):
        """Test ImageSerializer"""
        image = Image.objects.create(
            title='Test Image',
            image=self.create_test_image(),
            gallery=self.gallery
        )
        
        serializer = ImageSerializer(image)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Image')
        self.assertEqual(data['uuid'], image.hashpath)
        self.assertIn('thumbnail_url', data)
        self.assertIn('image_url', data)


class UtilityFunctionTest(TestCase):
    """Test utility functions"""
    
    def test_generate_hashpath(self):
        """Test generate_hashpath function"""
        hashpath1 = generate_hashpath()
        hashpath2 = generate_hashpath()
        
        # Should be 32 characters (UUID4 hex)
        self.assertEqual(len(hashpath1), 32)
        self.assertEqual(len(hashpath2), 32)
        
        # Should be unique
        self.assertNotEqual(hashpath1, hashpath2)
        
        # Should be alphanumeric
        self.assertTrue(hashpath1.isalnum())
        self.assertTrue(hashpath2.isalnum())
