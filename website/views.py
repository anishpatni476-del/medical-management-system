from decimal import Decimal

from django.conf import settings
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.db.models import Q, F,Count
from .models import Category, Supplier, Medicine, Message, Feedback, OwnerProfile,Purchase
from datetime import date, timedelta
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
from imagekitio import ImageKit
from django.views.decorators.csrf import csrf_exempt

imagekit = ImageKit(
    private_key=settings.IMAGEKIT_PRIVATE_KEY
)




# Create your views here.
@never_cache
def home(request):
    profile = OwnerProfile.objects.first()
    return render(request,'website/home.html',{"profile":profile})


@never_cache
def about(request):
    profile = OwnerProfile.objects.first()
    return render(request,'website/about.html',{"profile":profile})

@never_cache
def services(request):
    profile = OwnerProfile.objects.first()
    return render(request,'website/services.html',{"profile":profile})

@never_cache
def medicines(request):
    profile = OwnerProfile.objects.first()
    medicines = Medicine.objects.select_related("category").filter(
        stock_quantity__gt=0
    )
    search = request.GET.get('search')
    category = request.GET.get('category')

    if search:
        medicines= medicines.filter(
            Q(medicine_name__icontains=search)|
            Q(company_name__icontains=search)|
            Q(category__category_name__icontains=search)
        )
    if category:
        medicines = medicines.filter(category_id =category)

    categories = Category.objects.filter(status='Active')


    context = {
        "medicines":medicines,
        "categories":categories,
        "profile": profile,
    }
    return render(request,'website/medicines.html',context)

@never_cache
def contact(request):
    profile = OwnerProfile.objects.first()
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        Message.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        return redirect("contact")
    owner_profile = OwnerProfile.objects.first()
    context = {
        "owner_profile":owner_profile,
        "profile": profile,
    }
    return render(request,'website/contact.html',context)

@never_cache
def feedback(request):
    profile = OwnerProfile.objects.first()
    if request.method == 'POST':
        customer_name = request.POST.get("customer_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        Feedback.objects.create(
            customer_name=customer_name,
            email=email,
            phone_number=phone_number,
            rating=rating,
            comment=comment

        )

        messages.success(request,'Thank you! Your feedback has been submitted successfully.',extra_tags="public")
        return redirect("feedback")
    feedbacks = Feedback.objects.order_by('-created_at')[:6]
    return render(request,'website/feedback.html',{"feedbacks":feedbacks,"profile":profile})

@never_cache
def owner_login(request):
    if request.user.is_authenticated:
        return redirect("owner_dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print("username:",username)
        print("password:",password)
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect("owner_dashboard")
        else:
            messages.error(request,"Invalid username and password.")

    return render(request,'owner/login.html')



@never_cache
@login_required
def owner_dashboard(request):
    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.count()
    total_medicines = Medicine.objects.count()
    total_messages = Message.objects.count()
    total_feedback = Feedback.objects.count()
    total_purchase = Purchase.objects.count()
    recent_messeges = Message.objects.order_by('-created_at')[:5]
    recent_feedbacks = Feedback.objects.order_by('-created_at')[:5]
    all_low_stock_medicines = Medicine.objects.filter(stock_quantity__lte=F('minimum_stock'),
                                                  stock_quantity__gt=0
                                                  ).order_by('stock_quantity')
    low_stock_medicines = all_low_stock_medicines[:5]
    recent_purchase = Purchase.objects.select_related(
        "medicine","supplier"
    ).order_by('-created_at')[:5]
    today = date.today()
    next_30_days = today + timedelta(days=30)
    all_expiry_medicines = Medicine.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=next_30_days
    ).order_by('expiry_date')


    for medicine in all_expiry_medicines:
        medicine.days_left =(medicine.expiry_date - today).days

    expiry_medicines = all_expiry_medicines[:5]
    context = {
        "total_categories":total_categories,
        "total_suppliers":total_suppliers,
        "total_medicines":total_medicines,
        "total_messages":total_messages,
        "total_feedback":total_feedback,
        "total_purchase":total_purchase,
        "recent_messages":recent_messeges,
        "recent_feedbacks":recent_feedbacks,
        "low_stock_medicines":low_stock_medicines,
        "all_low_stock_medicines":all_low_stock_medicines,
        "expiry_medicines":expiry_medicines,
        "all_expiry_medicines":all_expiry_medicines,
        "recent_purchase":recent_purchase,
    }
    return render(request,"owner/dashboard.html",context)

@never_cache
@login_required
def owner_medicines(request):
    search = request.GET.get("search")
    medicines = Medicine.objects.all().order_by('-id')

    if search:
        medicines = medicines.filter(
            Q(medicine_name__icontains=search)|
            Q(company_name__icontains=search)|
            Q(batch_no__icontains=search)

        )
    paginator = Paginator(medicines, 10)
    page_number = request.GET.get('page')
    medicines = paginator.get_page(page_number)
    return render(request,"owner/medicines.html",{"medicines":medicines})

@never_cache
@login_required
def add_medicine(request):
    categories = Category.objects.filter(status="Active")
    suppliers = Supplier.objects.filter(status="Active")
    if request.method == "POST":
        medicine_name = request.POST.get('medicine_name').strip()
        category_id = request.POST.get('category')
        company_name = request.POST.get('company_name').strip()
        batch_no = request.POST.get('batch_no').strip()
        stock_quantity = request.POST.get('stock_quantity').strip()
        purchase_price = request.POST.get('purchase_price').strip()
        selling_price = request.POST.get('selling_price').strip()
        minimum_stock = request.POST.get('minimum_stock').strip()
        manufacturing_date = request.POST.get('manufacturing_date')
        expiry_date = request.POST.get('expiry_date')
        supplier_id = request.POST.get('supplier')
        medicine_image =request.FILES.get('medicine_image')
        description = request.POST.get('description').strip()

        context = {
            "categories":categories,
            "suppliers":suppliers,
            "form_data":request.POST,
            "selected_category":request.POST.get("category"),
            "selected_supplier":request.POST.get("supplier"),
        }

        if not stock_quantity.isdigit() or int(stock_quantity) < 0:
            messages.error(request, "Stock quantity must be 0 or greater.")
            return render(request, "owner/add_medicine.html", context)

        if not minimum_stock.isdigit() or int(minimum_stock) < 0:
            messages.error(request, "Minimum stock must be 0 or greater.")
            return render(request, "owner/add_medicine.html", context)

        try:
            purchase_price = Decimal(purchase_price)
            selling_price = Decimal(selling_price)
        except:
            messages.error(request, "Enter valid prices.")
            return render(request, "owner/add_medicine.html", context)

        if purchase_price < 0:
            messages.error(request, "Purchase price cannot be negative.")
            return render(request, "owner/add_medicine.html", context)

        if selling_price < purchase_price:
            messages.error(request, "Selling price cannot be less than purchase price.")
            return render(request, "owner/add_medicine.html", context)

        if manufacturing_date >= expiry_date:
            messages.error(request, "Expiry date must be after manufacturing date.")
            return render(request, "owner/add_medicine.html", context)


        if not medicine_name:
            messages.error(request, "Medicine name is required.")
            return render(request, "owner/add_medicine.html", context)

        if not category_id:
            messages.error(request, "Please select a category.")
            return render(request, "owner/add_medicine.html", context)

        if not company_name:
            messages.error(request, "Company name is required.")
            return render(request, "owner/add_medicine.html", context)

        if not supplier_id:
            messages.error(request, "Please select a supplier.")
            return render(request, "owner/add_medicine.html", context)



        if Medicine.objects.filter(
                medicine_name__iexact=medicine_name,
                batch_no__iexact=batch_no
        ).exists():
            messages.error(request, "This medicine with the same batch number already exists.")
            return render(request, "owner/add_medicine.html", context)
        category = Category.objects.get(id=category_id)
        supplier = Supplier.objects.get(id=supplier_id)

        Medicine.objects.create(
            medicine_name=medicine_name,
            category=category,
            company_name=company_name,
            batch_no=batch_no,
            stock_quantity=stock_quantity,
            purchase_price=purchase_price,
            selling_price=selling_price,
            minimum_stock=minimum_stock,
            manufacturing_date=manufacturing_date,
            expiry_date=expiry_date,
            supplier=supplier,
            medicine_image=medicine_image,
            description=description
        )
        messages.success(request,"Medicine added successfully.")
        return redirect('owner_medicines')
    return render(request,"owner/add_medicine.html",{"categories":categories,"suppliers":suppliers,"form_data":{}})

@never_cache
@login_required
def update_medicine(request,id):
    medicine = get_object_or_404(Medicine,id=id)
    categories = Category.objects.filter(status = "Active")
    suppliers = Supplier.objects.filter(status = "Active")

    if request.method == "POST":
        medicine.medicine_name = request.POST.get("medicine_name")
        medicine.category = Category.objects.get(id=request.POST.get("category"))
        medicine.company_name = request.POST.get("company_name")
        medicine.batch_no = request.POST.get("batch_no")
        medicine.stock_quantity = request.POST.get("stock_quantity")
        medicine.purchase_price = request.POST.get("purchase_price")
        medicine.selling_price = request.POST.get("selling_price")
        medicine.minimum_stock = request.POST.get("minimum_stock")
        medicine.manufacturing_date = request.POST.get("manufacturing_date")
        medicine.expiry_date = request.POST.get("expiry_date")
        medicine.supplier = Supplier.objects.get(id=request.POST.get("supplier"))
        medicine.description = request.POST.get("description")
        if request.FILES.get("medicine_image"):
            medicine.medicine_image = request.FILES.get("medicine_image")
        medicine.save()
        return redirect("owner_medicines")
    return render(request,"owner/update_medicine.html",
                  {"medicine":medicine,"categories":categories,"suppliers":suppliers})

@never_cache
@login_required
def delete_medicine(request,id):
    medicine = get_object_or_404(Medicine,id=id)
    medicine.delete()
    return redirect('owner_medicines')

@never_cache
@login_required
def owner_category(request):
    search = request.GET.get("search")

    categories = Category.objects.annotate(total_medicines=Count('medicine')).order_by('-id')
    if search:
        categories = categories.filter(
            Q(category_name__icontains=search)
        )
    paginator = Paginator(categories, 5)
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)
    return render(request,"owner/category.html",{"categories":categories})

@never_cache
@login_required
def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name').strip()
        description = request.POST.get('description').strip()
        status = request.POST.get('status')

        if not category_name:
            messages.error(request,"Category name is required.")
            return render(request,"owner/add_category.html")

        if Category.objects.filter(category_name__iexact=category_name).exists():
            messages.error(request,"Category already exists.")
            return render(request,"owner/add_category.html")


        Category.objects.create(
            category_name=category_name,
            description=description,
            status=status
        )
        messages.success(request,"Category added successfully.")
        return redirect('owner_category')
    return render(request,'owner/add_category.html')

@never_cache
@login_required
def update_category(request,id):
    category = get_object_or_404(Category,id=id)
    if request.method == "POST":
        category.category_name=request.POST.get('category_name')
        category.description=request.POST.get('description')
        category.status = request.POST.get('status')
        category.save()
        return redirect('owner_category')
    return render(request,'owner/update_category.html',{"category":category})

@never_cache
@login_required
def delete_category(request,id):
    category = get_object_or_404(Category,id=id)
    category.delete()
    return redirect("owner_category")



@never_cache
@login_required
def suppliers(request):
    search = request.GET.get("search")
    suppliers = Supplier.objects.all().order_by('-id')
    if search:
        suppliers = suppliers.filter(
            Q(company_name__icontains=search)|
            Q(contact_person__icontains=search)|
            Q(mobile_no__icontains=search)|
            Q(city__icontains=search)

                                     )

    paginator = Paginator(suppliers, 10)
    page_number = request.GET.get('page')
    suppliers = paginator.get_page(page_number)
    return render(request,'owner/suppliers.html',{"suppliers":suppliers})

@never_cache
@login_required
def add_supplier(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name').strip()
        contact_person = request.POST.get('contact_person').strip()
        mobile_no = request.POST.get('mobile_no').strip()
        email = request.POST.get('email').strip()
        gst_no = request.POST.get('gst_no').strip()
        address = request.POST.get('address').strip()
        city = request.POST.get('city').strip()
        status = request.POST.get('status')
        context = {"form_data": request.POST
                   }

        if not company_name:
            messages.error(request,"Company name is required.")
            return render(request,"owner/add_supplier.html",context)

        if not contact_person:
            messages.error(request,"Contact person is required.")
            return render(request,"owner/add_supplier.html",context)

        if not mobile_no.isdigit() or len(mobile_no) != 10:
            messages.error(request,"Enter a valid 10-digit mobile number.")
            return render(request, "owner/add_supplier.html",context)


        if Supplier.objects.filter(company_name__iexact=company_name).exists():
            messages.error(request,"Company already exists.")
            return render(request, "owner/add_supplier.html",context)

        if gst_no and Supplier.objects.filter(gst_no__iexact=gst_no).exists():
            messages.error(request,"GST Number already exists.")
            return render(request, "owner/add_supplier.html",context)



        Supplier.objects.create(
            company_name=company_name,
            contact_person=contact_person,
            mobile_no=mobile_no,
            email=email,
            gst_no=gst_no,
            address=address,
            city=city,
            status=status
        )

        messages.success(request,"Supplier added successfully.")
        return redirect('suppliers')

    return render(request,'owner/add_supplier.html',{"form_data":{}})

@never_cache
@login_required
def update_supplier(request,id):
    supplier = get_object_or_404(Supplier,id=id)
    if request.method == "POST":
        supplier.company_name =request.POST.get('company_name')
        supplier.contact_person = request.POST.get('contact_person')
        supplier.mobile_no = request.POST.get('mobile_no')
        supplier.email = request.POST.get('email')
        supplier.gst_no = request.POST.get('gst_no')
        supplier.address = request.POST.get('address')
        supplier.city = request.POST.get('city')
        supplier.status = request.POST.get('status')
        supplier.save()
        return redirect('suppliers')
    return render(request,'owner/update_supplier.html',{"supplier":supplier})

@never_cache
@login_required
def delete_supplier(request,id):
    supplier = get_object_or_404(Supplier,id=id)
    supplier.delete()
    return redirect('suppliers')

@never_cache
@login_required
def owner_messages(request):
    search = request.GET.get('search')
    messages = Message.objects.all().order_by('-created_at')
    if search:
        messages = messages.filter(
            Q(name__icontains=search)|
            Q(email__icontains=search)|
            Q(phone__icontains=search)
        )
    paginator = Paginator(messages, 5)
    page_number = request.GET.get('page')
    messages = paginator.get_page(page_number)
    return  render(request,'owner/messages.html',{"messages":messages})

@never_cache
@login_required
def delete_message(request,id):
    message = get_object_or_404(Message,id=id)
    message.delete()
    return redirect("owner_messages")

@never_cache
@login_required
def owner_feedback(request):
    search = request.GET.get("search")
    feedbacks = Feedback.objects.all().order_by('-created_at')
    if search:
        feedbacks = feedbacks.filter(
            Q(customer_name__icontains=search)|
            Q(phone_number__icontains=search)|
            Q(email__icontains=search)
        )
    paginator = Paginator(feedbacks, 5)
    page_number = request.GET.get('page')
    feedbacks = paginator.get_page(page_number)
    return render(request,'owner/owner_feedback.html',{"feedbacks":feedbacks})


@never_cache
@login_required
def delete_feedback(request,id):
    feedback = get_object_or_404(Feedback,id=id)
    feedback.delete()
    messages.success(request,"Feedback deleted successfully.")
    return redirect("owner_feedback")


@never_cache
@login_required
def owner_reports(request):
    total_medicines = Medicine.objects.count()

    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.count()
    low_stock = Medicine.objects.filter(
        stock_quantity__lte=F("minimum_stock"),
        stock_quantity__gt=0
    ).count()
    expired_medicines = Medicine.objects.filter(
        expiry_date__lt=date.today()
    ).count()
    out_of_stock = Medicine.objects.filter(
        stock_quantity=0
    ).count()
    total_messages = Message.objects.count()
    total_feedback = Feedback.objects.count()
    context = {'total_medicines':total_medicines,
               "total_categories":total_categories,
               "total_suppliers":total_suppliers,
               "low_stock":low_stock,
               "expired_medicines":expired_medicines,
               "out_of_stock":out_of_stock,
               "total_messages":total_messages,
               "total_feedback":total_feedback}
    return render(request,'owner/reports.html',context)


@never_cache
@login_required
def owner_profile(request):
    if request.user.is_authenticated:
        profile, created = OwnerProfile.objects.get_or_create(
            user=request.user
        )

    return render(request,"owner/owner_profile.html",{"profile":profile})



@never_cache
@login_required
def update_profile(request):
    profile, created = OwnerProfile.objects.get_or_create(
        user=request.user
    )
    if request.method == "POST":
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.username = request.POST.get('username')
        request.user.email = request.POST.get('email')
        request.user.save()

        profile.mobile_number =  request.POST.get("mobile_number")
        profile.medical_store_name = request.POST.get("medical_store_name")
        profile.medical_store_address = request.POST.get("medical_store_address")
        profile.business_hours = request.POST.get('business_hours')

        if request.FILES.get("profile_photo"):
            profile.profile_photo = request.FILES.get("profile_photo")

        if request.FILES.get("home_hero_image"):
            profile.home_hero_image = request.FILES.get("home_hero_image")

        if request.FILES.get("home_about_image"):
            profile.home_about_image = request.FILES.get("home_about_image")

        if request.FILES.get("about_page_image"):
            profile.about_page_image = request.FILES.get("about_page_image")

        if request.FILES.get("services_page_image"):
            profile.services_page_image = request.FILES.get("services_page_image")

        if request.FILES.get("medicines_page_image"):
            profile.medicines_page_image = request.FILES.get("medicines_page_image")

        if request.FILES.get("contact_page_image"):
            profile.contact_page_image = request.FILES.get("contact_page_image")

        if request.FILES.get("feedback_page_image"):
            profile.feedback_page_image = request.FILES.get("feedback_page_image")


        profile.save()
        messages.success(request,"Profile updated successfully")
        return redirect("owner_profile")

    return render(request,"owner/update_profile.html",{"profile":profile})
@never_cache
@login_required
def purchase_list(request):
    search = request.GET.get('search')
    purchases = Purchase.objects.all().order_by('-id')
    if search:
        purchases = purchases.filer(
            Q(invoice_number__icontains=search)|
            Q(medicines__medicine_name__icontains=search)|
            Q(suppliers__company_name__icontains=search)

        )
    paginator = Paginator(purchases, 10)
    page_number = request.GET.get('page')
    purchases = paginator.get_page(page_number)

    return render(request,"owner/purchase.html",{"purchases":purchases})

@never_cache
@login_required
def add_purchase(request):
    suppliers = Supplier.objects.filter(status='Active')
    medicines = Medicine.objects.all()
    if request.method == 'POST':
        supplier = Supplier.objects.get(id=request.POST.get("supplier"))
        medicine = Medicine.objects.get(id=request.POST.get("medicine"))
        invoice_number = request.POST.get("invoice_number")
        purchase_price = Decimal(request.POST.get("purchase_price"))
        quantity = int(request.POST.get("quantity"))
        gst_percentage = Decimal(request.POST.get("gst_percentage"))
        purchase_date = request.POST.get("purchase_date")

        subtotal = purchase_price * quantity
        gst_amount = (subtotal * gst_percentage)/ Decimal("100")
        total_amount = subtotal + gst_amount


        Purchase.objects.create(
            supplier=supplier,
            medicine=medicine,
            invoice_number=invoice_number,
            purchase_price=purchase_price,
            quantity=quantity,
            gst_percentage=gst_percentage,
            total_amount=total_amount,
            purchase_date=purchase_date
        )

        medicine.stock_quantity += quantity
        medicine.purchase_price = purchase_price
        medicine.save()


        messages.success(request,"Purchase added successfully")
        return redirect("purchase_list")

    return render(request,"owner/add_purchase.html",{"suppliers":suppliers,"medicines":medicines})

@never_cache
@login_required
def update_purchase(request,id):
    purchase = get_object_or_404(Purchase,id=id)
    suppliers = Supplier.objects.filter(status='Active')
    medicines = Medicine.objects.all()
    if request.method == "POST":
        purchase.medicine.stock_quantity -= purchase.quantity
        purchase.medicine.save()

        supplier = Supplier.objects.get(id=request.POST.get("supplier"))
        medicine = Medicine.objects.get(id=request.POST.get("medicine"))
        purchase.supplier=supplier
        purchase.medicine=medicine
        purchase.invoice_number= request.POST.get("invoice_number")
        purchase.purchase_price=Decimal(request.POST.get("purchase_price"))
        purchase.quantity=int(request.POST.get("quantity"))
        purchase.gst_percentage=Decimal(request.POST.get("gst_percentage"))
        purchase.purchase_date=request.POST.get("purchase_date")
        subtotal = purchase.purchase_price * purchase.quantity
        purchase.gst_amount = (subtotal * purchase.gst_percentage)/Decimal("100")
        purchase.total_amount=subtotal+purchase.gst_amount
        purchase.save()

        medicine.stock_quantity += purchase.quantity
        medicine.purchase_price = purchase.purchase_price
        medicine.save()

        messages.success(request,"Purchase updated successfully ")
        return redirect("purchase_list")
    return render(request,"owner/update_purchase.html",{"purchase":purchase,"suppliers":suppliers,"medicines":medicines})

@never_cache
@login_required
def delete_purchase(request,id):
    purchase = get_object_or_404(Purchase,id=id)
    medicine = purchase.medicine
    medicine.stock_quantity -= purchase.quantity

    if medicine.stock_quantity < 0:
        medicine.stock_quantity = 0
    medicine.save()

    purchase.delete()
    messages.success(request,"purchase deleted successfully.")
    return redirect("purchase_list")

@never_cache
@login_required
def stock_management(request):
    search = request.GET.get("search")
    today = date.today()
    next_30_days = today + timedelta(days=30)
    medicines = Medicine.objects.all().order_by('-id')
    if search:
        medicines = medicines.filter(
            Q(medicine_name__icontains=search)|
            Q(company_name__icontains=search)|
            Q(batch_no__icontains=search)
        )
    paginator = Paginator(medicines,10)
    page_number = request.GET.get("page")
    medicines = paginator.get_page(page_number)
    return render(request,'owner/stock_management.html',{"medicines":medicines,"today":today,"next_30_days":next_30_days})

@never_cache
@login_required
def download_report_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response["Content-Disposition"] = 'attachment; filename="Medical_store_report_pdf"'
    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    elements = []
    title = Paragraph("<b> Medical Store Management Report</b>",styles["Title"])
    elements.append(title)
    elements.append(
        Paragraph(f'Report Date:{date.today()}',styles['Normal'])
    )
    elements.append(Paragraph("<br/>",styles["Normal"]))
    total_medicines = Medicine.objects.count()
    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.count()
    total_messages = Message.objects.count()
    total_feedback = Feedback.objects.count()
    low_stock = Medicine.objects.filter(
        stock_quantity__lte=F("minimum_stock"),
        stock_quantity__gt=0
    ).count()
    out_of_stock = Medicine.objects.filter(
        stock_quantity=0
    ).count()
    expired_medicines = Medicine.objects.filter(
        expiry_date__lt = date.today()
    ).count()

    data =[
        ["Report","Total"],
        ["Total Medicines",total_medicines],
        ["Total Categories",total_categories],
        ["Total Suppliers",total_suppliers],
        ["Low Stock Medicines",low_stock],
        ["Out Of Stock Medicnes",out_of_stock],
        ["Expired Medicines",expired_medicines],
        ["Customer Messages",total_messages],
        ["Customer Feedback",total_feedback],
    ]

    table = Table(data,colWidths=[4*inch,2*inch])
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.darkgreen),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ("BACKGROUND",(0,1),(-1,-1),colors.beige),
        ('ALIGN',(0,0),(-1,-1),"CENTER"),
        ('FONTNAME',(0,0),(-1,0),"Helvetica-Bold"),
        ("BOTTOMPADDING",(0,0),(-1,0),10)
    ]))
    elements.append(table)
    doc.build(elements)
    return response
@never_cache
@login_required
def delete_multiple_medicines(request):
    if request.method == "POST":
        medicine_ids = request.POST.getlist('medicine_ids')
        if medicine_ids:
            Medicine.objects.filter(id__in=medicine_ids).delete()
            messages.success(request,"Selected medicines deleted successfully.")
        else:
            messages.warning(request,"Please select at least one medicine.")
    return redirect("owner_medicines")

@never_cache
@login_required
def owner_logout(request):
    logout(request)
    return redirect("owner_login")


@never_cache
@login_required
def update_images(request):
    profile = request.user.ownerprofile
    if request.method == "POST":

        if request.FILES.get("home_hero_image"):
            profile.home_hero_image= request.FILES.get("home_hero_image")

        if request.FILES.get("home_about_image"):
            profile.home_about_image= request.FILES.get("home_about_image")

        if request.FILES.get("about_page_image"):
            profile.about_page_image= request.FILES.get("about_page_image")

        if request.FILES.get("services_page_image"):
            profile.services_page_image= request.FILES.get("services_page_image")

        if request.FILES.get("medicines_page_image"):
            profile.medicines_page_image= request.FILES.get("medicines_page_image")

        if request.FILES.get("contact_page_image"):
            profile.contact_page_image= request.FILES.get("contact_page_image")

        if request.FILES.get("feedback_page_image"):
            profile.feedback_page_image= request.FILES.get("feedback_page_image")

        profile.save()
        messages.success(request,"Website images updated successfully.",extra_tags="owner")
        return redirect("owner_profile")

    return render(request,"owner/update_images.html",{"profile":profile})


