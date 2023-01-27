from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
import os
from apps.cart.models import Cart
from apps.user_profile.models import UserProfile 
from apps.wishlist.models import WishList

class UserAccountManager(BaseUserManager):              #FUNCTION PARA CREAR UN USUARIO VIA "DJOSER-REACT"
    def create_user(self, email, password=None,**extra_fields):
        if not email:
            raise ValueError('Users must have an email address')   #SI NO ES UN EMAIL ALGO SALIO MAL

        email = self.normalize_email(email)    #PARA TRANSFORMAR A OBJETO LEIBLE A BD
        user = self.model(email=email, **extra_fields)  

        user.set_password(password)
        user.save()

        shopping_cart = Cart.objects.create(user=user)
        shopping_cart.save()

        profile = UserProfile.objects.create(user=user)   #CON ESTO CREAMOS UN PERFIL DE USUARIO CADA Q UN USU ES CREADO
        profile.save()    

        wishlist = WishList.objects.create(user=user)
        wishlist.save()

        return user

    def create_superuser(self, email, password,**extra_fields):
        user = self.create_user(email, password,**extra_fields)

        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class UserAccount(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)        
    last_name = models.CharField(max_length=255)        
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  #UN USURIO NORMAL NO ES MIEMBRO DE STAFF DEFINIDA EN ESTA CREACION DE ORIGEN

    objects = UserAccountManager()                 #PARA INTERACTUAR CON EL REGISTRO DE JOSER-REACT

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] 

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email        
