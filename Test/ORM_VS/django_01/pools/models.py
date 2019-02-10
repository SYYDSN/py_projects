from django.db import models


# Create your models here.


class Dept(models.Model):
    name = models.CharField(max_length=128, verbose_name="部门名")


class Person(models.Model):
    name = models.CharField(max_length=128, verbose_name="人名")
    age = models.IntegerField()
    dept_id = models.ForeignKey(to=Dept, on_delete=None, related_name="dept_id")

    class Meta:
        db_table = "django_person"


    @classmethod
    def random(cls):
        pass


if __name__ == "__main__":
    d = Dept(name="前台")
    d.save()
    pass
