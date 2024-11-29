from typing import Type

from django.db.models.manager import BaseManager

from core.domain.users.models import User, UserFactory


class UserServices:
    @staticmethod
    def get_user_factory() -> Type[UserFactory]:
        return UserFactory

    @staticmethod
    def get_user_repo() -> BaseManager[User]:
        return User.objects
