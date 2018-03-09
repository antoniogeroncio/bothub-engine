import json
import random
import uuid

from django.test import TestCase, RequestFactory
from django.test.client import MULTIPART_CONTENT
from rest_framework.authtoken.models import Token

from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common.models import RepositoryExampleEntity
from bothub.common import languages

from ..views import NewRepositoryViewSet
from ..views import MyRepositoriesViewSet
from ..views import RepositoryViewSet
from ..views import NewRepositoryExampleViewSet
from ..views import RepositoryExampleViewSet
from ..views import RepositoryAuthorizationView
from ..views import NewRepositoryExampleEntityViewSet
from ..views import RepositoryExampleEntityViewSet
from ..views import NewRepositoryTranslatedExampleViewSet
from ..views import RepositoryTranslatedExampleViewSet
from ..views import NewRepositoryTranslatedExampleEntityViewSet
from ..views import RepositoryTranslatedExampleEntityViewSet
from ..views import RepositoryExamplesViewSet


class APITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            'fake@user.com',
            'user',
            '123456')
        self.user_token, create = Token.objects.get_or_create(user=self.user)

        self.other_user = User.objects.create_user(
            'fake2@user.com',
            'user2',
            '123456')
        self.other_user_token, create = Token.objects.get_or_create(
            user=self.other_user)

        self.category = RepositoryCategory.objects.create(
            name='category')

        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='test',
            language=languages.LANGUAGE_EN)
        self.repository.categories.add(self.category)

        self.private_repository = Repository.objects.create(
            owner=self.user,
            slug='private',
            is_private=True,
            name='private test',
            language=languages.LANGUAGE_EN)
        self.private_repository.categories.add(self.category)

        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_EN),
            text='hey Douglas',
            intent='greet')

        self.entity = RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=4,
            end=11,
            entity='name')

        self.translated = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=languages.LANGUAGE_PT,
            text='olá Douglas')

    # moved to tests.repository.NewRepositoryTestCase.request
    def _new_repository_request(self, slug, name, language, categories):
        request = self.factory.post(
            '/api/repository/new/',
            {
                'slug': slug,
                'name': name,
                'language': language,
                'categories': categories,
            },
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = NewRepositoryViewSet.as_view({'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    # moved to tests.repository.NewRepositoryTestCase.test_okay
    def test_new_repository(self):
        test_slug = 'test_{}'.format(random.randint(100, 9999))
        (response, content_data) = self._new_repository_request(
            test_slug,
            'test',
            languages.LANGUAGE_EN,
            [self.category.id])
        self.assertEqual(response.status_code, 201)
        self.assertEqual(content_data.get('slug'), test_slug)

    # moved to tests.repository.NewRepositoryTestCase.test_unique_slug
    def test_new_repository_unique_slug(self):
        test_slug = 'test_{}'.format(random.randint(100, 9999))
        (response_1, content_data_1) = self._new_repository_request(
            test_slug,
            'test',
            languages.LANGUAGE_EN,
            [self.category.id])
        self.assertEqual(response_1.status_code, 201)
        (response_2, content_data_2) = self._new_repository_request(
            test_slug,
            'test',
            languages.LANGUAGE_EN,
            [self.category.id])
        self.assertEqual(response_2.status_code, 400)

    def test_my_repositories(self):
        request = self.factory.get(
            '/api/my-repositories/',
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = MyRepositoriesViewSet.as_view({'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content_data.get('results')[0].get('uuid'),
            str(self.repository.uuid))

    # moved to tests.repository.RetrieveRepositoryTestCase
    def test_repository_retrieve(self):
        request = self.factory.get(
            '/api/repository/{}/'.format(self.repository.uuid),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryViewSet.as_view({'get': 'retrieve'})(
            request,
            pk=str(self.repository.uuid))
        response.render()
        content_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_data.get('uuid'), str(self.repository.uuid))

    def test_repository_languages_status(self):
        request = self.factory.get(
            '/api/repository/{}/languagesstatus/'.format(
                self.repository.uuid),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryViewSet.as_view(
            {'get': 'languagesstatus'})(
                request,
                pk=str(self.repository.uuid))
        self.assertEqual(response.status_code, 200)

    def _repository_authorization_request(self, token=None, **data):
        token = token or self.user_token.key
        request = self.factory.post(
            '/api/authorization/',
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(token),
            })
        response = RepositoryAuthorizationView.as_view(
            {'post': 'create'})(request)
        response.render()
        return response

    def test_repository_authorization(self):
        response = self._repository_authorization_request(
            repository_uuid=self.repository.uuid)
        self.assertEqual(response.status_code, 200)

    def test_repository_authorization_private_and_authorized(self):
        response = self._repository_authorization_request(
            repository_uuid=self.private_repository.uuid)
        self.assertEqual(response.status_code, 200)

    def test_repository_authorization_private_and_unauthorized(self):
        response = self._repository_authorization_request(
            repository_uuid=self.private_repository.uuid,
            token=self.other_user_token.key)
        self.assertEqual(response.status_code, 403)

    def test_repository_authorization_without_repository_uuid(self):
        response = self._repository_authorization_request()
        self.assertEqual(response.status_code, 400)

    def test_repository_authorization_repository_does_not_exist(self):
        response = self._repository_authorization_request(
            repository_uuid=uuid.uuid4())
        self.assertEqual(response.status_code, 404)

    def test_repository_authorization_repository_uuid_invalid(self):
        response = self._repository_authorization_request(
            repository_uuid='invalid')
        self.assertEqual(response.status_code, 400)

    # moved to tests.repository.UpdateRepositoryTestCase.request
    def _update_repository_request(self, repository_uuid, data):
        request = self.factory.put(
            '/api/repository/{}/'.format(repository_uuid),
            self.factory._encode_data(data, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryViewSet.as_view(
            {'put': 'update'})(request, pk=repository_uuid)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    # moved to tests.repository.UpdateRepositoryTestCase
    def test_repository_update(self):
        new_slug = 'test_{}'.format(random.randint(1, 10))
        (response, content_data) = self._update_repository_request(
            str(self.repository.uuid),
            {
                'slug': new_slug,
                'is_private': True,
                'name': self.repository.name,
                'language': self.repository.language,
                'categories': [self.category.id],
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_data.get('slug'), new_slug)
        self.assertEqual(content_data.get('is_private'), True)

    # moved to tests.repository.UpdateRepositoryTestCase
    def test_repository_cannot_update_uuid(self):
        new_uuid = str(uuid.uuid4())
        new_slug = 'test_{}'.format(random.randint(1, 10))
        (response, content_data) = self._update_repository_request(
            str(self.repository.uuid),
            {
                'uuid': new_uuid,
                'slug': new_slug,
                'name': self.repository.name,
                'language': self.repository.language,
                'categories': [self.category.id],
            })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(content_data.get('uuid'), new_uuid)

    # moved to tests.repository.DestroyRepositoryTestCase
    def test_repository_destroy(self):
        request = self.factory.delete(
            '/api/repository/{}/'.format(self.repository.uuid),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryViewSet.as_view(
            {'delete': 'destroy'})(request, pk=str(self.repository.uuid))
        response.render()
        self.assertEqual(response.status_code, 204)

    def _new_repository_example_request(self, data):
        request = self.factory.post(
            '/api/example/new/',
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = NewRepositoryExampleViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_new_repository_example(self):
        response, content_data = self._new_repository_example_request({
            'repository_uuid': self.repository.uuid,
            'text': 'hey',
            'intent': 'greet',
        })
        self.assertEqual(response.status_code, 201)

    def test_new_repository_example_without_repository_uuid(self):
        response, content_data = self._new_repository_example_request({
            'text': 'hey',
            'intent': 'greet',
        })
        self.assertEqual(response.status_code, 400)

    def test_new_repository_example_repository_does_not_exists(self):
        response, content_data = self._new_repository_example_request({
            'repository_uuid': uuid.uuid4(),
            'text': 'hey',
            'intent': 'greet',
        })
        self.assertEqual(response.status_code, 404)

    def test_new_repository_example_invalid_repository_uuid(self):
        response, content_data = self._new_repository_example_request({
            'repository_uuid': 'invalid',
            'text': 'hey',
            'intent': 'greet',
        })
        self.assertEqual(response.status_code, 400)

    def test_repository_example_retrieve(self):
        request = self.factory.get(
            '/api/example/{}/'.format(self.example.id),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryExampleViewSet.as_view(
            {'get': 'retrieve'})(request, pk=self.example.id)
        response.render()
        self.assertEqual(response.status_code, 200)

    def test_repository_example_destroy(self):
        request = self.factory.delete(
            '/api/example/{}/'.format(self.example.id),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryExampleViewSet.as_view(
            {'delete': 'destroy'})(request, pk=self.example.id)
        response.render()
        self.assertEqual(response.status_code, 204)
        self.example = RepositoryExample.objects.get(id=self.example.id)
        self.assertEqual(
            self.example.deleted_in,
            self.repository.current_update(
                self.example.repository_update.language))

    def test_repository_example_already_deleted(self):
        self.example.delete()
        request = self.factory.delete(
            '/api/example/{}/'.format(self.example.id),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryExampleViewSet.as_view(
            {'delete': 'destroy'})(request, pk=self.example.id)
        response.render()
        self.assertEqual(response.status_code, 500)

    def _new_repository_example_entity_request(self, data):
        request = self.factory.post(
            '/api/entity/new/',
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = NewRepositoryExampleEntityViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_new_repository_example_entity(self):
        response, content_data = self._new_repository_example_entity_request({
            'repository_example': self.example.id,
            'start': 4,
            'end': 11,
            'entity': 'name',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(content_data.get('value'), 'Douglas')

    def test_repository_examples_entity(self):
        request = self.factory.get(
            '/api/entity/{}/'.format(self.entity.id),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryExampleEntityViewSet.as_view(
            {'get': 'retrieve'})(request, pk=self.example.id)
        self.assertEqual(response.status_code, 200)

    def test_translate_example(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_EN),
            text='hi',
            intent='greet')
        request = self.factory.post(
            '/api/translate-example/',
            {
               'original_example': example.id,
               'language': languages.LANGUAGE_PT,
               'text': 'oi',
            },
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = NewRepositoryTranslatedExampleViewSet.as_view(
            {'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)

    def test_translated_example(self):
        request = self.factory.get(
            '/api/translated/{}/'.format(self.translated.id),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryTranslatedExampleViewSet.as_view(
            {'get': 'retrieve'})(request, pk=self.translated.id)
        self.assertEqual(response.status_code, 200)

    def _new_translated_example_entity_request(self, data):
        request = self.factory.post(
            '/api/translated-entity/new/',
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = NewRepositoryTranslatedExampleEntityViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_new_translated_example_entity(self):
        response, content_data = self._new_translated_example_entity_request({
            'repository_translated_example': self.translated.id,
            'start': 4,
            'end': 11,
            'entity': 'name',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(content_data.get('value'), 'Douglas')

    def test_translated_example_entity(self):
        translated_entity = RepositoryTranslatedExampleEntity.objects.create(
            repository_translated_example=self.translated,
            start=4,
            end=11,
            entity='name')
        request = self.factory.get(
            '/api/translated-entity/{}/'.format(translated_entity.id),
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryTranslatedExampleEntityViewSet.as_view(
            {'get': 'retrieve'})(request, pk=translated_entity.id)
        self.assertEqual(response.status_code, 200)

    def _examples_request(self, data):
        request = self.factory.get(
            '/api/examples/',
            data,
            **{
                'HTTP_AUTHORIZATION': 'Token {}'.format(self.user_token.key),
            })
        response = RepositoryExamplesViewSet.as_view(
            {'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_examples(self):
        response, content_data = self._examples_request({
            'repository_uuid': self.repository.uuid,
        })
        self.assertEqual(response.status_code, 200)

    def test_examples_without_repository_uuid(self):
        response, content_data = self._examples_request({})
        self.assertEqual(response.status_code, 400)

    def test_examples_with_repository_does_not_exist(self):
        response, content_data = self._examples_request({
            'repository_uuid': uuid.uuid4(),
        })
        self.assertEqual(response.status_code, 404)

    def test_examples_with_invalid_uuid(self):
        response, content_data = self._examples_request({
            'repository_uuid': 'invalid',
        })
        self.assertEqual(response.status_code, 400)

    def test_examples_language_filter(self):
        response_1, content_data_1 = self._examples_request({
            'repository_uuid': self.repository.uuid,
            'language': languages.LANGUAGE_EN,
        })
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(content_data_1.get('count'), 1)

        response_2, content_data_2 = self._examples_request({
            'repository_uuid': self.repository.uuid,
            'language': languages.LANGUAGE_NL,
        })
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(content_data_2.get('count'), 0)

    def test_examples_has_translation_filter(self):
        response_1, content_data_1 = self._examples_request({
            'repository_uuid': self.repository.uuid,
            'has_translation': True,
        })
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(content_data_1.get('count'), 1)

        response_2, content_data_2 = self._examples_request({
            'repository_uuid': self.repository.uuid,
            'has_translation': False,
        })
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(content_data_2.get('count'), 0)
