from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator

class AccountManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, nickname, email, password, *args,**kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            nickname=nickname,
            email=email,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, *args,**kwargs):
        
        if password is None:
            raise TypeError('Superuser must have a password.')
        

        user = self.model(
            nickname="관리자", 
            email=email, 
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        
        return user

class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    nickname = models.CharField(
        max_length=20,
        null=False,
        unique=False
    )
    image = models.ImageField(
        blank=True, 
        null=True, 
        upload_to="uploads"
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = AccountManager()
    
    USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['nickname']
    
class RegisterCodeBuffer(models.Model):
    id = models.AutoField(primary_key=True) #고유번호
    
    email = models.EmailField(
        max_length=255,
    )
    code = models.IntegerField(
        default=123456,
        validators=[MinValueValidator(6),MaxValueValidator(6)]
    )