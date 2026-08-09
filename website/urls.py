from django.urls import path
from .import views

urlpatterns =[
    path("",views.home,name='home'),
    path('about/', views.about,name='about'),
    path('services/', views.services,name='services'),
    path('medicines/',views.medicines, name='medicines'),
    path('contact/',views.contact,name='contact'),
    path('feedback/',views.feedback,name='feedback'),
    path('owner/login/',views.owner_login,name='owner_login'),



    path('owner/dashboard/',views.owner_dashboard,name='owner_dashboard'),
    path('owner/medicines/',views.owner_medicines,name='owner_medicines'),
    path('owner/category/',views.owner_category,name='owner_category'),
    path('owner/add_category',views.add_category,name='add_category'),
    path('owner/add_medicine',views.add_medicine,name='add_medicine'),
    path('owner/medicines/update/<int:id>/',views.update_medicine,name='update_medicine'),
    path('owner/medicines/delete/<int:id>/',views.delete_medicine,name='delete_medicine'),
    path('owner/suppliers',views.suppliers,name='suppliers'),
    path('owner/add_supplier',views.add_supplier,name='add_supplier'),
    path('owner/owner_messages',views.owner_messages,name='owner_messages'),
    path('owner/message/delete/<int:id>/',views.delete_message,name='delete_message'),
    path('owner/owner_feedback',views.owner_feedback,name='owner_feedback'),
    path('owner/feedback/delete/<int:id>/',views.delete_feedback,name='delete_feedback'),
    path('owner/category/update/<int:id>/',views.update_category,name='update_category'),
    path('owner/category/delete/<int:id>/',views.delete_category,name='delete_category'),
    path('owner/suppliers/update/<int:id>/',views.update_supplier, name="update_supplier"),
    path('owner/supplier/delete/<int:id>/',views.delete_supplier,name='delete_supplier'),
    path('owner/owner_reports/',views.owner_reports,name='owner_reports'),
    path('owner/owner_profile',views.owner_profile,name='owner_profile'),
    path('owner/update_profile/',views.update_profile,name='update_profile'),
    path('owner/purchase',views.purchase_list,name='purchase_list'),
    path('owner/add_purchase/',views.add_purchase,name='add_purchase'),
    path('owner/purchase/update/<int:id>/',views.update_purchase,name='update_purchase'),
    path('owner/purchase/delete/<int:id>',views.delete_purchase,name='delete_purchase'),
    path('owner/stock_management/',views.stock_management,name="stock_management"),
    path('report/pdf/',views.download_report_pdf,name="download_report_pdf"),
    path('delete_multiple_medicines',views.delete_multiple_medicines,name='delete_multiple_medicines'),
    path('owner/owner_logout/',views.owner_logout,name="owner_logout"),
    path("owner/update_images/",views.update_images,name="update_images"),



]