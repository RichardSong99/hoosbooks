from django.db import models
import datetime 
from django.utils import timezone
from decimal import *
from PIL import Image
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.
class Agent(models.Model):
    #first and last name, appropriately capitalized
    name = models.CharField(max_length = 100)
    #computing ID, all lowercase
    compID = models.CharField(max_length = 20, unique = True)
    timestamp  = models.DateTimeField(default = timezone.now, blank = True, null = True)


    def __str__(self):
        string = self.name + " (" + self.compID + ")"
        return string

class Buyer(models.Model):
    name = models.CharField(max_length = 100)
    #computing ID, all lowercase
    compID = models.CharField(max_length = 20)
    timestamp  = models.DateTimeField(default = timezone.now, blank = True, null = True)
    message = models.TextField()
    phone = models.CharField(max_length= 11)

    def __str__(self):
        string = self.name + " (" + self.compID + ")"
        return string

class Seller(AbstractBaseUser, Agent):
    active = models.BooleanField(default = True)
    admin = False
    USERNAME_FIELD      = 'compID'
    #USERNAME_FIELD and password are required by default
    REQUIRED_FIELDS     = ['name', 'password']

    def email_register(self):
        string = "Hello, " + self.name.title() + "! Your HoosBooks account has been created.\n\n"
        string += "Here is your account information: \n"
        string += "Name: " + self.name.title() + "\n"
        string += "Computing ID: " + self.compID + "\n"
        string += "Password: " + self.password + '\n\n'

        string += "Thank you for using HoosBooks. You are ready to list books on your account to be sold. "
        return string

class UserManager(BaseUserManager):
    def create_user(self, name, compID, password):
        if not name:
            raise ValueError('Users must have a name')
        if not compID:
            raise ValueError('Users must have a computing ID')
        
        user_obj = self.model()
        user_obj.set_password(password)
        user_obj.save(using = self._db)
        return user_obj
    
    def create_superuser(self, name, compID, password):
        user = self.create_superuser(name, compID, password)
        user.save(using = self._db)
        admin = True
        return user

class Item(models.Model):
    title = models.CharField(max_length = 200)
    author = models.CharField(max_length  = 100)
    seller = models.ForeignKey(Seller, on_delete = models.SET_NULL, null = True, blank = True)
    prof_last_name = models.CharField(max_length = 50, blank = True, null = True, default = "")
    course_dept = models.CharField(max_length = 7, blank = True, null = True, default ="")
    course_number = models.IntegerField(blank = True, null = True, default = "")
    quality = models.CharField(max_length = 50)
    price = models.DecimalField(max_digits= 5, decimal_places=2)
    buyer = models.ManyToManyField(Buyer, blank = True)
    time_added = models.DateTimeField(auto_now_add=True, blank = True)
    image = models.ImageField(null = True, blank = True, upload_to = "gallery")
    
    def __str__(self):
        string = self.title + ", written by " + self.author
        return string

    def summary(self):
        twoplaces = Decimal(10) ** -2
        string = "Author: " + self.author.title() + "<br />"
        string += "Price: $" + str(Decimal(self.price).quantize(twoplaces, context= Context(traps = [Inexact]))) + "<br />"        
        string += "Quality: " + self.quality.title() + "<br />"
        string += 'Seller: ' + self.seller.name.title()
        return string
    
    def supplemental(self):
        string = "Course: " + self.course_dept.upper() + " " + str(self.course_number) + "<br />"
        string += "Professor: " + self.prof_last_name.title() + "<br />"
        string += "Date listed: " + str(self.time_added.date()) 
        return string
    
    #content
    def content(self):
        string = "Details: \n"
        string += "Title: " + self.title.title() + '\n'

        string_info = (self.summary() + "\n" + self.supplemental()).replace("<br />", "\n")

        string += string_info + '\n\n'

        string += "Thank you for using HoosBooks!"

        return string


    def email(self, command):
        string = "Hello, " + self.seller.name.title() + "! \n"
        if command == 'ADD':
            string += "You have added " + self.__str__() + " to your HoosBooks account.\n\n"
        elif command == 'EDIT':
            string += "You have made the following changes to " + self.__str__() + " in your HoosBooks account. \n\n"
        elif command == 'DELETE':
            string += "You have deleted " + self.__str__() + " from your HoosBooks account. \n\n"

        string += self.content()

        return string

    def email_request(self, buyer, command):
        string = ""
        if command == 'REQUEST-S':
            string += "Hello, " + self.seller.name.title() + "! \n"
            string += buyer.name.title() + " is interested in your book " + self.__str__() + "\n\n"
            string += "Here is his/her contact information: \n"
        elif command == 'REQUEST-B':
            string += "Hello, " + buyer.name.title() + "! \n"
            string += "Thank you for requesting the book " + self.__str__() + " from " + self.seller.name.title() + ". \n\n"
            string += self.seller.name.title()  + " contact: " + self.seller.compID + '@virginia.edu' + "\n\n"
            string += "Record:"

        string += "Name: " + buyer.name.title() +'\n'
        string += "Email: " + buyer.compID + "@virginia.edu" + "\n"
        string += "Phone: " + buyer.phone + "\n\n"

        string += "Message from " + buyer.name.title() + ": \n"
        string += buyer.message + '\n\n'

        string += self.content()

        return string


    