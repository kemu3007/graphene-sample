import graphene
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"
        description = "Django Default User"


class ContenttypeType(DjangoObjectType):
    class Meta:
        model = ContentType
        fields = "__all__"
        description = "Django Contenttype"


class Query(graphene.ObjectType):
    users = graphene.List(UserType, description="ユーザ情報一覧取得API", deprecation_reason="セキュリティ上存在してはいけないAPIのためdeprecated")
    contenttypes = graphene.List(ContenttypeType, description="コンテンツタイプ一覧取得API")

    def resolve_users(self, info):
        return User.objects.all()

    def resolve_contenttypes(self, info):
        return ContentType.objects.all()


schema = graphene.Schema(query=Query)
