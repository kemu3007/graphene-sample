from typing import Dict, List, Union

import graphene
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Model, Prefetch, QuerySet
from graphene.utils.str_converters import to_snake_case
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug
from graphene_django.utils import get_model_fields
from graphql.execution.base import ResolveInfo
from graphql.language import ast as graphql_ast

from apps.models import Article


class ArticleType(DjangoObjectType):
    class Meta:
        model = Article
        fields = "__all__"
        description = Article.__doc__


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"
        description = User.__doc__


class ContenttypeType(DjangoObjectType):
    class Meta:
        model = ContentType
        fields = "__all__"
        description = ContentType.__doc__


class QueryOptimizer:
    """紐付きのあるモデルをクエリの内容によって自動的にselect_related/prefetch_relatedを行う"""

    def __init__(self) -> None:
        self.select_related_fields: List[str] = []
        self.prefetch_objects: List[Prefetch] = []

    def optimize_query(self, info: Union[ResolveInfo, graphql_ast.Field], queryset: QuerySet) -> QuerySet:
        """クエリの最適化処理"""
        field: graphql_ast.Field = info.field_asts[0] if isinstance(info, ResolveInfo) else info
        self._extract_related_fields(queryset.model, field)
        return queryset.select_related(*self.select_related_fields).prefetch_related(*self.prefetch_objects)

    def _extract_related_fields(self, model: type[Model], field: graphql_ast.Field, prefix: str = ""):
        """リクエストフィールド内の関連モデルを参照/逆参照に応じて再起的に分類"""

        fields: graphql_ast.SelectionSet = field.selection_set
        model_fields: Dict[str, models.Field] = {key: field for (key, field) in get_model_fields(model)}
        for field in filter(lambda x: x.selection_set is not None, fields.selections):
            related_name = to_snake_case(f"{prefix}__{field.name.value}" if prefix else field.name.value)
            field_name = to_snake_case(field.name.value)
            model_field = model_fields[field_name]
            if model_field.many_to_many or model_field.one_to_many:
                self.prefetch_objects.append(
                    Prefetch(
                        related_name, QueryOptimizer().optimize_query(field, model_field.related_model.objects.all())
                    )
                )
                continue
            self.select_related_fields.append(related_name)
            self._extract_related_fields(model_field.related_model, field, related_name)


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="_debug")
    users = graphene.List(UserType, description="ユーザ情報一覧取得API", deprecation_reason="セキュリティ上存在してはいけないAPIのためdeprecated")
    contenttypes = graphene.List(ContenttypeType, description="コンテンツタイプ一覧取得API")
    articles = graphene.List(ArticleType, description="記事一覧取得API")

    def resolve_users(self, info):
        return QueryOptimizer().optimize_query(User.objects.all())

    def resolve_contenttypes(self, info):
        return QueryOptimizer().optimize_query(info, ContentType.objects.all())

    def resolve_articles(self, info: ResolveInfo):
        return QueryOptimizer().optimize_query(info, Article.objects.all())


schema = graphene.Schema(query=Query)
