from rest_framework import routers

from .views import NewRepositoryViewSet
from .views import MyRepositoriesViewSet
from .views import RepositoryViewSet
from .views import NewRepositoryExampleViewSet
from .views import RepositoryExampleViewSet
from .views import NewRepositoryTranslatedExampleViewSet
from .views import RepositoryTranslatedExampleViewSet
from .views import NewRepositoryTranslatedExampleEntityViewSet
from .views import RepositoryTranslatedExampleEntityViewSet
from .views import RepositoryExamplesViewSet
from .views import RegisterUserViewSet
from .views import UserViewSet
from .views import LoginViewSet
from .views import ChangePasswordViewSet
from .views import RequestResetPassword
from .views import ResetPassword
from .views import MyUserProfile
from .views import UserProfile
from .views import Categories
from .views import RepositoriesViewSet


class Router(routers.SimpleRouter):
    def get_lookup_regex(self, viewset, lookup_prefix=''):
        lookup_fields = getattr(viewset, 'lookup_fields', None)
        if lookup_fields:
            base_regex = '(?P<{lookup_prefix}{lookup_url_kwarg}>[^/.]+)'
            return '/'.join(map(
                lambda x: base_regex.format(
                    lookup_prefix=lookup_prefix,
                    lookup_url_kwarg=x),
                lookup_fields))
        return super().get_lookup_regex(viewset, lookup_prefix)


router = Router()
router.register('repository/new', NewRepositoryViewSet)
router.register('my-repositories', MyRepositoriesViewSet)
router.register('repository', RepositoryViewSet)
router.register('example/new', NewRepositoryExampleViewSet)
router.register('example', RepositoryExampleViewSet)
router.register('translate-example', NewRepositoryTranslatedExampleViewSet)
router.register('translation', RepositoryTranslatedExampleViewSet)
router.register('translation-entity/new',
                NewRepositoryTranslatedExampleEntityViewSet)
router.register('translation-entity',
                RepositoryTranslatedExampleEntityViewSet)
router.register('examples', RepositoryExamplesViewSet)
router.register('register', RegisterUserViewSet)
router.register('profile', UserViewSet)
router.register('login', LoginViewSet)
router.register('change-password', ChangePasswordViewSet)
router.register('forgot-password', RequestResetPassword)
router.register('reset-password', ResetPassword)
router.register('my-profile', MyUserProfile)
router.register('user-profile', UserProfile)
router.register('categories', Categories)
router.register('repositories', RepositoriesViewSet)