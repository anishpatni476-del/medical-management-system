from django.db import models

from django.contrib.auth.models import User
from .storage import ImageKitStorage

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True, null=True)
    description = models.TextField(blank=True,null=True)
    status = models.CharField(max_length=10,choices=[('Active','Active'),('Inactive','Inactive'),],default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name

class Supplier(models.Model):
    company_name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    gst_no = models.CharField(blank=True, max_length=15, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=20,blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ],
                              default='Active')
    created_at =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class Medicine(models.Model):
    medicine_name = models.CharField(max_length=150)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    company_name = models.CharField(max_length=150)
    batch_no = models.CharField(max_length=50,blank=True, null=True)
    stock_quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True)
    minimum_stock = models.PositiveIntegerField(blank=True, null=True)
    manufacturing_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE)
    medicine_image = models.ImageField(upload_to='medicine_images/',blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.medicine_name


class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message =models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Feedback(models.Model):
    customer_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True,null=True)
    phone_number = models.CharField(blank=True,max_length=15, null=True)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name


class OwnerProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,blank=True,null=True)
    profile_photo = models.ImageField(
        upload_to='owner_profile/',
        blank=True,
        null=True
    )
    mobile_number = models.CharField(max_length=15,blank=True,null=True)
    medical_store_name = models.CharField(max_length=150,blank=True,null=True)
    medical_store_address = models.TextField(blank=True,null=True)
    business_hours = models.TextField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    home_hero_image = models.ImageField(upload_to="public_site_images", storage=ImageKitStorage,null=True,blank=True)
    home_about_image = models.ImageField(upload_to="public_site_images",storage=ImageKitStorage, null=True, blank=True)
    about_page_image = models.ImageField(upload_to="public_site_images",storage=ImageKitStorage, null=True, blank=True)
    services_page_image = models.ImageField(upload_to="public_site_images",storage=ImageKitStorage, null=True, blank=True)
    medicines_page_image = models.ImageField(upload_to="public_site_images",storage=ImageKitStorage, null=True, blank=True)
    contact_page_image = models.ImageField(upload_to="public_site_images",storage=ImageKitStorage, null=True, blank=True)
    feedback_page_image = models.ImageField(upload_to="public_site_images",storage=ImageKitStorage, null=True, blank=True)




    def __str__(self):
        return self.user.username


class Purchase(models.Model):
    medicine = models.ForeignKey(Medicine,on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50,blank=True,null=True)
    purchase_price = models.DecimalField(max_digits=10,decimal_places=2)
    quantity = models.PositiveIntegerField()
    gst_percentage = models.DecimalField(
        max_digits=5,decimal_places=2,default=0
    )
    gst_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    total_amount = models.DecimalField(
        max_digits=12,decimal_places=2
    )
    purchase_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine.medicine_name}-{self.purchase_date}"


