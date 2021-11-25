from django.db import models
from django.contrib.auth.models import User, UserManager
from django.contrib import admin
from django.utils import timezone


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=75)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    objects = UserManager()

    def __unicode__(self):
        return self.customer_name


class Computer(models.Model):
    PersonalComputer = 'Personal Computer'
    Monoblock = 'Monoblock'
    Laptop = 'Laptop'
    computer_types = {
        (PersonalComputer, 'Personal computer'),
        (Monoblock, 'Monoblock'),
        (Laptop, 'Laptop'),
    }
    name = models.CharField(max_length=255, unique=True, primary_key=True)
    price = models.IntegerField(null=True, default=0)
    description = models.TextField(
        max_length=500, default='No description yet')
    type = models.CharField(
        max_length=30, choices=computer_types, default=PersonalComputer)
    # pic = models.ImageField(upload_to='media/', default='media/ts.jpg')
    quantity = models.IntegerField(null=True, default=0)
    pic = models.ImageField(upload_to='media/', null=True, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    date = models.DateTimeField(default=timezone.now)
    items = models.ManyToManyField(Computer, through='BelongTo')
    code = models.AutoField(max_length=6, unique=True, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total = models.DecimalField(
        decimal_places=2, max_digits=10, unique=False, default=0.0)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return str(self.code)


class BelongTO(models.Model):
    item = models.ForeignKey(Computer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True)
    id = models.CharField(unique=True, primary_key=True, max_length=255)

    def __str__(self):
        return self.id
