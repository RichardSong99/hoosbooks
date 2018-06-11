from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import Seller, Buyer, Item
from django.views.generic import TemplateView
from django import forms
from market.forms import SearchForm, OrderForm, RegisterForm, SellerLoginForm, AddEditItemForm, SuggestionForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.mail import EmailMessage
from django.utils import timezone
from smtplib import SMTPException

class logged_in_status:
    logged_in = False

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the market index")

#searching for items
class SearchView(TemplateView):
    #template name
    template_name = 'market/search.html'
        
    def get(self, request):
        form = SearchForm()
        item_list = Item.objects.all()
        args = {'form': form, 'item_list': item_list}
        return render(request, self.template_name, args)

    def post(self, request):
        
        self.search_clicked = True
        
        form = SearchForm(request.POST)
        if form.is_valid():
            course_dept = form.cleaned_data['course_dept']
            course_number = form.cleaned_data['course_number']
            title= form.cleaned_data['title']

        #search for relevant results
        item_list = searcher(course_dept, course_number, title, form) 

        args = {
            'form':form,
            'item_list': item_list,
        }
        return render(request, self.template_name, args)

#return item_list of relevant items searched for
def searcher(course_dept, course_number, title, form):
    item_list = Item.objects.all()
    if form.cleaned_data['course_dept']:
        item_list = item_list.filter(course_dept__icontains = course_dept)
    if form.cleaned_data['course_number']:
        item_list = item_list.filter(course_number = course_number)
    if form.cleaned_data['title']:
        item_list = item_list.filter(title__icontains = title)
    
    return item_list

#order view
class OrderView(TemplateView):
    #template_name
    template_name = 'market/order.html'
    
    def get_queryset(self):
        return Item.objects.get(item_id = self.kwargs['item_id'])

    def get(self, request, item_id):
        #seller name
        item = Item.objects.get(id = item_id)
        seller = item.seller

        #default values
        default_message = "Hello " + seller.name.title()  + ", I am interested in your textbook " + item.title +'. Would it be possible to meet you somewhere to pick it up? Thank you!'
        default_dict = {'message': default_message}

        form = OrderForm(initial = default_dict)
        context = {'form':form, 'item':item}
        return render(request, self.template_name, context = context)

    def post(self, request, item_id):
        form= OrderForm(request.POST)
        if form.is_valid():
            #save buyer in database
            name = form.cleaned_data['name']
            compID = form.cleaned_data['compID']
            message = form.cleaned_data['message']
            phone = form.cleaned_data['phone']
            timestamp = timezone.now()
            buyer = Buyer(name = name, compID= compID, message=message, phone=phone, timestamp=timestamp)
            buyer.save()
            #add buyer to item.buyer
            item = Item.objects.get(id = item_id)
            item.buyer.add(buyer)
            item.save()
            name = form.cleaned_data['name']

            seller = item.seller
            #email
            seller_email = seller.compID+"@virginia.edu"
            buyer_email = buyer.compID + "@virginia.edu"
            #send email to seller from server email
            email1 = EmailMessage(
                'Buyer Interested in Item',
                item.email_request(buyer, "REQUEST-S"),
                to = [seller_email,]
            )
            email1.send()

            #send email to buyer
            email2 = EmailMessage(
                'Request Confirmation',
                item.email_request(buyer, "REQUEST-B"),
                to = [buyer_email,]
            )
            email2.send()

        #alert after form submission
        alert = "Thank you for submitting. An email will be sent to you and the seller to coordinate the transaction. "

        args = {
            'form': form,
            'item': item,
            'name': form.cleaned_data['name'],
            'compID':form.cleaned_data['compID'],
            'message':form.cleaned_data['message'],
            'phone':form.cleaned_data['phone'],
            'alert':alert
        }
        return render(request, self.template_name, args)

#register view
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            seller = form.save()
            seller_email = seller.compID + "@virginia.edu"
            email = EmailMessage(
                'Account Created',
                seller.email_register(),
                to = [seller_email,],
            )
            email.send()
            return redirect(login_view)
        else:
            args = {'form': form}
            return render(request, 'market/reg_form.html', args)
    else:
        form = RegisterForm()
        args =  {'form': form}
        return render(request, 'market/reg_form.html', args) #should redirect to login html

#login view
def login_view(request):
    display_error = False #for message

    if request.method == 'POST':
        form = SellerLoginForm(request.POST,request.FILES)
        if form.is_valid():
            compID = form.cleaned_data['compID']
            password = form.cleaned_data['password']
            potential_seller = Seller.objects.filter(compID = compID)
            #validate attempt to login
            if potential_seller.exists() and potential_seller[0].password == password:
                logged_in_status.logged_in = True
                seller = potential_seller[0]
                item_list = Item.objects.filter(seller = seller)
                args = {
                    'seller': seller,
                    'item_list': item_list
                }
                return render(request, 'market/dashboard.html', args)
            else:
                display_error = True
                return render(request, 'market/login.html', {'form': form, 'display_error': display_error})
    else:
        form = SellerLoginForm()
    return render(request, 'market/login.html', {'form': form})

#logout view
def logout(request):
    logged_in_status.logged_in = False
    return redirect(login_view)

#delete existing item
def deleteitem(request,item_id):
    if logged_in_status.logged_in:
        item = Item.objects.get(id = item_id)
        seller = item.seller

        #EMAIL
        seller_email = seller.compID+"@virginia.edu"
        #send email to seller from server email
        email = EmailMessage(
            'Item Deleted',
            item.email("DELETE"),
            to = [seller_email,]
        )      
        email.send()  

        item.delete()
        item_list = Item.objects.filter(seller = seller)
        args = {
            'seller': seller,
            'item_list': item_list
        }
        return render(request, 'market/dashboard.html', args)

    else:
        return redirect(login_view)

#add new item
def additem(request, seller_id):
    if logged_in_status.logged_in:
        seller = Seller.objects.get(id = seller_id)
        if request.method == 'POST':
            form = AddEditItemForm(request.POST, request.FILES)
            if form.is_valid():
                #save item
                title = form.cleaned_data['title']
                author = form.cleaned_data['author']
                course_dept = form.cleaned_data['course_dept']
                course_number = form.cleaned_data['course_number']
                prof_last_name = form.cleaned_data['prof_last_name']
                quality = form.cleaned_data['quality']
                price = form.cleaned_data['price']
                if 'image' in request.FILES:
                    image = request.FILES['image']
                else:
                    image = None

                item = Item(title = title, author = author, course_dept =course_dept, course_number=course_number, prof_last_name=prof_last_name, quality=quality,price=price, image=image, seller=seller)
                item.save()

                seller_email = seller.compID+"@virginia.edu"
                #send email to seller from server email
                email = EmailMessage(
                    'Item Added',
                    item.email("ADD"),
                    to = [seller_email,]
                )

                email.send()
                
                item_list = Item.objects.filter(seller = seller)
                args = {
                    'seller': seller,
                    'item_list': item_list
                }
                return render(request, 'market/dashboard.html', args)
        else:
            form = AddEditItemForm()
            return render(request, 'market/addedititem.html', {'form': form})
    else:
        return redirect(login_view)

#edit existing item
def edititem(request, item_id):
    if logged_in_status.logged_in:
        item = Item.objects.get(id = item_id)
        seller = item.seller
        if request.method == 'POST':
            form = AddEditItemForm(request.POST, request.FILES)
            if form.is_valid():
                #update all fields
                item.title = form.cleaned_data['title']
                item.author = form.cleaned_data['author']
                item.course_dept = form.cleaned_data['course_dept']
                item.course_number = form.cleaned_data['course_number']
                item.prof_last_name = form.cleaned_data['prof_last_name']
                item.quality = form.cleaned_data['quality']
                item.price = form.cleaned_data['price']
                #image
                image_upload = request.FILES.get('image', False)
                if image_upload != False:
                    item.image = request.FILES['image']
 
                item.save()

                #email
                seller_email = seller.compID+"@virginia.edu"
                #send email to seller from server email
                email = EmailMessage(
                    'Item Changed',
                    item.email("EDIT"),
                    to = [seller_email,]
                )
                email.send()

                item_list = Item.objects.filter(seller = seller)
                args = {
                    'seller': seller,
                    'item_list': item_list
                }
                return render(request, 'market/dashboard.html', args)
            else:
                item_list = Item.objects.filter(seller = seller)
                args = {
                    'seller': seller,
                    'item_list': item_list
                }
                return render(request, 'market/dashboard.html', args)
        else:
            default_args = {
                'title':item.title.title(),
                'author':item.author.title(),
                'course_dept':item.course_dept.upper(),
                'course_number':item.course_number,
                'prof_last_name':item.prof_last_name.title(),
                'quality': item.quality.title(),
                'price': item.price,
                'image': item.image
            }
            form = AddEditItemForm(initial = default_args)
            return render(request, 'market/addedititem.html', {'form': form})
    #not logged in
    else:
        return redirect(login_view)

def about(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            suggestion = form.cleaned_data['suggestion']
            message = 'Thank you very much for your feedback!'

            args = {
                'form':  form,
                'message': message
            }

            #email
            dest = "hoosbooks.uva@gmail.com"
            mail = "Sent from " + name + "\n" + suggestion
            #send email to seller from server email
            email = EmailMessage(
                'Suggestion',
                mail,
                to = [dest,]
            )
            email.send()        

            return render(request, 'market/about.html', args)
        
    else:
        form = SuggestionForm()
        message = 'Dedicated to improving your experience on HoosBooks.'

        args = {
                'form':  form,
                'message': message
        }
        return render(request, 'market/about.html', args)