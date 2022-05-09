from django.db import models


class User(models.Model):
    id = models.CharField(max_length=66, primary_key=True) # kakao user id <기본키>
    status = models.FloatField(default=0) # kakao user status
    menu = models.IntegerField(default=0) # kakao user menu
    b_choice = models.CharField(max_length=10,default='none') # Kakao user choice (barcode yes or no)
    d_choice = models.CharField(max_length=10,default='none') # Kakao user choice (description yes or no)
    cicode= models.IntegerField(default=0) # current item code
    citype = models.CharField(max_length=10,default='none') # current item type
    ciname = models.CharField(max_length=50,default='none') # current item name
    cidesc = models.CharField(max_length=50,default='none') # current item description
    cinum = models.IntegerField(default=0) # current item number
    cidate = models.DateField(null=True) # current item date

    class Meta:
        db_table = "user"


class Item(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE) # kakao user id <외래키>
    icode = models.IntegerField(default=0) # item code
    itype = models.CharField(max_length=10,default='none') # item type
    iname = models.CharField(max_length=50,default='none') # item name
    idesc = models.CharField(max_length=50,default='none') # item description
    inum = models.IntegerField(default=0) # item number
    idate = models.DateField(null=True)  # item date

    class Meta:
        db_table = "item"

