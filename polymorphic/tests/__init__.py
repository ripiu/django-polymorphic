# -*- coding: utf-8 -*-

import django
import uuid
from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType

from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from polymorphic.query import PolymorphicQuerySet
from polymorphic.showfields import ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent

try:
    from django.db.models import UUIDField
except ImportError:
    # django<1.8
    from polymorphic.tools_for_tests import UUIDField


class PlainA(models.Model):
    field1 = models.CharField(max_length=10)


class PlainB(PlainA):
    field2 = models.CharField(max_length=10)


class PlainC(PlainB):
    field3 = models.CharField(max_length=10)


class Model2A(ShowFieldType, PolymorphicModel):
    field1 = models.CharField(max_length=10)
    polymorphic_showfield_deferred = True


class Model2B(Model2A):
    field2 = models.CharField(max_length=10)


class Model2C(Model2B):
    field3 = models.CharField(max_length=10)


class Model2D(Model2C):
    field4 = models.CharField(max_length=10)


class ModelExtraA(ShowFieldTypeAndContent, PolymorphicModel):
    field1 = models.CharField(max_length=10)


class ModelExtraB(ModelExtraA):
    field2 = models.CharField(max_length=10)


class ModelExtraC(ModelExtraB):
    field3 = models.CharField(max_length=10)


class ModelExtraExternal(models.Model):
    topic = models.CharField(max_length=10)


class ModelShow1(ShowFieldType, PolymorphicModel):
    field1 = models.CharField(max_length=10)
    m2m = models.ManyToManyField('self')


class ModelShow2(ShowFieldContent, PolymorphicModel):
    field1 = models.CharField(max_length=10)
    m2m = models.ManyToManyField('self')


class ModelShow3(ShowFieldTypeAndContent, PolymorphicModel):
    field1 = models.CharField(max_length=10)
    m2m = models.ManyToManyField('self')


class ModelShow1_plain(PolymorphicModel):
    field1 = models.CharField(max_length=10)


class ModelShow2_plain(ModelShow1_plain):
    field2 = models.CharField(max_length=10)


class Base(ShowFieldType, PolymorphicModel):
    field_b = models.CharField(max_length=10)


class ModelX(Base):
    field_x = models.CharField(max_length=10)


class ModelY(Base):
    field_y = models.CharField(max_length=10)


class Enhance_Plain(models.Model):
    field_p = models.CharField(max_length=10)


class Enhance_Base(ShowFieldTypeAndContent, PolymorphicModel):
    base_id = models.AutoField(primary_key=True)
    field_b = models.CharField(max_length=10)


class Enhance_Inherit(Enhance_Base, Enhance_Plain):
    field_i = models.CharField(max_length=10)


class RelationBase(ShowFieldTypeAndContent, PolymorphicModel):
    field_base = models.CharField(max_length=10)
    fk = models.ForeignKey('self', null=True, related_name='relationbase_set')
    m2m = models.ManyToManyField('self')


class RelationA(RelationBase):
    field_a = models.CharField(max_length=10)


class RelationB(RelationBase):
    field_b = models.CharField(max_length=10)


class RelationBC(RelationB):
    field_c = models.CharField(max_length=10)


class RelatingModel(models.Model):
    many2many = models.ManyToManyField(Model2A)


class One2OneRelatingModel(PolymorphicModel):
    one2one = models.OneToOneField(Model2A)
    field1 = models.CharField(max_length=10)


class One2OneRelatingModelDerived(One2OneRelatingModel):
    field2 = models.CharField(max_length=10)


class ModelUnderRelParent(PolymorphicModel):
    field1 = models.CharField(max_length=10)
    _private = models.CharField(max_length=10)


class ModelUnderRelChild(PolymorphicModel):
    parent = models.ForeignKey(ModelUnderRelParent, related_name='children')
    _private2 = models.CharField(max_length=10)


class MyManagerQuerySet(PolymorphicQuerySet):

    def my_queryset_foo(self):
        return self.all()  # Just a method to prove the existance of the custom queryset.


class MyManager(PolymorphicManager):
    queryset_class = MyManagerQuerySet

    def get_queryset(self):
        return super(MyManager, self).get_queryset().order_by('-field1')

    def my_queryset_foo(self):
        return self.all().my_queryset_foo()

    # Django <= 1.5 compatibility
    get_query_set = get_queryset


class ModelWithMyManager(ShowFieldTypeAndContent, Model2A):
    objects = MyManager()
    field4 = models.CharField(max_length=10)


class ModelWithMyManagerNoDefault(ShowFieldTypeAndContent, Model2A):
    objects = PolymorphicManager()
    my_objects = MyManager()
    field4 = models.CharField(max_length=10)


class ModelWithMyManagerDefault(ShowFieldTypeAndContent, Model2A):
    my_objects = MyManager()
    objects = PolymorphicManager()
    field4 = models.CharField(max_length=10)


if django.VERSION >= (1, 7):
    class ModelWithMyManager2(ShowFieldTypeAndContent, Model2A):
        objects = MyManagerQuerySet.as_manager()
        field4 = models.CharField(max_length=10)


class MROBase1(ShowFieldType, PolymorphicModel):
    objects = MyManager()
    base_1_id = models.AutoField(primary_key=True)
    field1 = models.CharField(max_length=10)  # needed as MyManager uses it


class MROBase2(MROBase1):
    pass  # Django vanilla inheritance does not inherit MyManager as _default_manager here


class MROBase3(models.Model):
    base_3_id = models.AutoField(primary_key=True)
    objects = PolymorphicManager()


class MRODerived(MROBase2, MROBase3):
    pass


class ParentModelWithManager(PolymorphicModel):
    pass


class ChildModelWithManager(PolymorphicModel):
    # Also test whether foreign keys receive the manager:
    fk = models.ForeignKey(ParentModelWithManager, related_name='childmodel_set')
    objects = MyManager()


class PlainMyManagerQuerySet(QuerySet):

    def my_queryset_foo(self):
        return self.all()  # Just a method to prove the existance of the custom queryset.


class PlainMyManager(models.Manager):

    def my_queryset_foo(self):
        return self.get_queryset().my_queryset_foo()

    def get_queryset(self):
        return PlainMyManagerQuerySet(self.model, using=self._db)

    # Django <= 1.5 compatibility
    get_query_set = get_queryset


class PlainParentModelWithManager(models.Model):
    pass


class PlainChildModelWithManager(models.Model):
    fk = models.ForeignKey(PlainParentModelWithManager, related_name='childmodel_set')
    objects = PlainMyManager()


class MgrInheritA(models.Model):
    mgrA = models.Manager()
    mgrA2 = models.Manager()
    field1 = models.CharField(max_length=10)


class MgrInheritB(MgrInheritA):
    mgrB = models.Manager()
    field2 = models.CharField(max_length=10)


class MgrInheritC(ShowFieldTypeAndContent, MgrInheritB):
    pass


class BlogBase(ShowFieldTypeAndContent, PolymorphicModel):
    name = models.CharField(max_length=10)


class BlogA(BlogBase):
    info = models.CharField(max_length=10)


class BlogB(BlogBase):
    pass


class BlogEntry(ShowFieldTypeAndContent, PolymorphicModel):
    blog = models.ForeignKey(BlogA)
    text = models.CharField(max_length=10)


class BlogEntry_limit_choices_to(ShowFieldTypeAndContent, PolymorphicModel):
    blog = models.ForeignKey(BlogBase)
    text = models.CharField(max_length=10)


class ModelFieldNameTest(ShowFieldType, PolymorphicModel):
    modelfieldnametest = models.CharField(max_length=10)


class InitTestModel(ShowFieldType, PolymorphicModel):
    bar = models.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        kwargs['bar'] = self.x()
        super(InitTestModel, self).__init__(*args, **kwargs)


class InitTestModelSubclass(InitTestModel):

    def x(self):
        return 'XYZ'

# models from github issue


class Top(PolymorphicModel):
    name = models.CharField(max_length=50)


class Middle(Top):
    description = models.TextField()


class Bottom(Middle):
    author = models.CharField(max_length=50)


class UUIDProject(ShowFieldTypeAndContent, PolymorphicModel):
    uuid_primary_key = UUIDField(primary_key=True, default=uuid.uuid1)
    topic = models.CharField(max_length=30)


class UUIDArtProject(UUIDProject):
    artist = models.CharField(max_length=30)


class UUIDResearchProject(UUIDProject):
    supervisor = models.CharField(max_length=30)


class UUIDPlainA(models.Model):
    uuid_primary_key = UUIDField(primary_key=True, default=uuid.uuid1)
    field1 = models.CharField(max_length=10)


class UUIDPlainB(UUIDPlainA):
    field2 = models.CharField(max_length=10)


class UUIDPlainC(UUIDPlainB):
    field3 = models.CharField(max_length=10)

# base -> proxy


class ProxyBase(PolymorphicModel):
    some_data = models.CharField(max_length=128)


class ProxyChild(ProxyBase):

    class Meta:
        proxy = True


class NonProxyChild(ProxyBase):
    name = models.CharField(max_length=10)

# base -> proxy -> real models


class ProxiedBase(ShowFieldTypeAndContent, PolymorphicModel):
    name = models.CharField(max_length=10)


class ProxyModelBase(ProxiedBase):

    class Meta:
        proxy = True


class ProxyModelA(ProxyModelBase):
    field1 = models.CharField(max_length=10)


class ProxyModelB(ProxyModelBase):
    field2 = models.CharField(max_length=10)


# test bad field name
# class TestBadFieldModel(ShowFieldType, PolymorphicModel):
#    instance_of = models.CharField(max_length=10)

# validation error: "polymorphic.relatednameclash: Accessor for field 'polymorphic_ctype' clashes
# with related field 'ContentType.relatednameclash_set'." (reported by Andrew Ingram)
# fixed with related_name
class RelatedNameClash(ShowFieldType, PolymorphicModel):
    ctype = models.ForeignKey(ContentType, null=True, editable=False)

# class with a parent_link to superclass, and a related_name back to subclass


class TestParentLinkAndRelatedName(ModelShow1_plain):
    superclass = models.OneToOneField(ModelShow1_plain, parent_link=True, related_name='related_name_subclass')


class CustomPkBase(ShowFieldTypeAndContent, PolymorphicModel):
    b = models.CharField(max_length=1)


class CustomPkInherit(CustomPkBase):
    custom_id = models.AutoField(primary_key=True)
    i = models.CharField(max_length=1)


class DateModel(PolymorphicModel):

    date = models.DateTimeField()


# Import tests
from .test_admin import *
from .test_orm import *
from .test_multidb import *
from .test_regression import *

