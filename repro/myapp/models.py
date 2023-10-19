from django.db import models

# Create your models here.

class PrimaryModelManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class SomePrimaryModel(models.Model):
    code = models.CharField(max_length=10, unique=True)

    def natural_key(self):
        return (self.code,)

    objects = PrimaryModelManager()


class SecondaryModelManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class SomeSecondaryModel(models.Model):
    code = models.CharField(max_length=10, unique=True)

    def natural_key(self):
        return (self.code,)

    objects = SecondaryModelManager()
