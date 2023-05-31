from django.db import models
from django.core.validators import MinLengthValidator

class Todo(models.Model):
    id = models.AutoField(primary_key=True) #고유번호
    writer = models.CharField(max_length=255) #작성자
    year = models.IntegerField() #년
    month = models.IntegerField() #월
    day = models.IntegerField() #일
    title = models.CharField(max_length=20) #내용
    description = models.TextField(blank=True) #설명
    done = models.BooleanField(default=False) #완료여부
    time = models.CharField(max_length=4, validators=[MinLengthValidator(4)], default='9999') #시간
    color = models.IntegerField(default=0) #색상

class ColorPriority(models.Model):
    id = models.AutoField(primary_key=True) #고유번호
    writer = models.CharField(max_length=255) #작성자
    priority = models.IntegerField(default=123456)
    USERNAME_FIELD = 'writer'

class PriorityName(models.Model):
    id = models.AutoField(primary_key=True) #고유번호
    writer = models.CharField(max_length=255) #작성자
    names = models.JSONField(unique=True)