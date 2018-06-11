from django import forms
from django.core.validators import EMPTY_VALUES
from django.core.exceptions import ValidationError
from .models import Item, Buyer, Seller
from django.contrib.auth.forms import ReadOnlyPasswordHashField 

class SearchForm(forms.Form):
    title = forms.CharField(label="Title", max_length=50, required = False)
    course_dept = forms.CharField(label = "Course Department",max_length=10, required = False)
    course_number = forms.IntegerField(label = "Course Number", required = False)
    #form formatting
    title.widget.attrs.update({'class': 'form-control', 'placeholder': 'Wealth of Nations', 'style':'width:50%'} )
    course_dept.widget.attrs.update({'class': 'form-control', 'placeholder': 'ECON', 'style':'width:30%'})
    course_number.widget.attrs.update({'class': 'form-control', 'placeholder': '2110', 'style':'width:30%'})


class OrderForm(forms.Form):
    name = forms.CharField(label = 'Name', max_length=50)
    compID = forms.CharField(label = 'Computing ID (for communication)', max_length=7)
    message = forms.CharField(widget = forms.Textarea, label = 'Message to Seller')
    phone = forms.CharField(max_length = 10)

    name.widget.attrs.update({'class': 'form-control', 'placeholder': 'Richard Song', 'style':'width:50%'} )
    compID.widget.attrs.update({'class': 'form-control', 'placeholder': 'rbs5cs', 'style':'width:50%'} )
    message.widget.attrs.update({'class': 'form-control', 'style':'width:50%', 'style':'height:100px'} )
    phone.widget.attrs.update({'class': 'form-control', 'placeholder': '5555555555', 'style':'width:50%'} )



class RegisterForm(forms.ModelForm):
    name = forms.CharField(label = 'Name')
    compID = forms.CharField(label = 'Computing ID (for communication)')
    password = forms.CharField(widget = forms.PasswordInput)
    password2 = forms.CharField(label = 'Confirm password', widget = forms.PasswordInput)

    name.widget.attrs.update({'class': 'form-control', 'placeholder': 'Richard Song', 'style':'width:50%'})
    compID.widget.attrs.update({'class': 'form-control', 'placeholder': 'rbs5cs', 'style':'width:50%'})
    password.widget.attrs.update({'class': 'form-control', 'style':'width:50%'})
    password2.widget.attrs.update({'class': 'form-control', 'style':'width:50%'})


    class Meta:
        model = Seller
        fields = ['name','compID', 'password']
    
    def clean(self):
        #comp ID
        cleaned_data = super(RegisterForm, self).clean()

        compID = cleaned_data['compID']
        qs = Seller.objects.filter(compID = compID)
        if qs.exists():
            raise forms.ValidationError("Computing ID is taken")
        #password
        password = cleaned_data["password"]
        password2 = cleaned_data["password2"]
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data

class SellerLoginForm(forms.Form):
    compID = forms.CharField(label = "Computing ID")
    password = forms.CharField(widget = forms.PasswordInput)

    compID.widget.attrs.update({'class': 'form-control', 'placeholder': 'rbs5cs', 'style':'width:30%'})
    password.widget.attrs.update({'class': 'form-control', 'placeholder': '********', 'style':'width:30%'})


class AddEditItemForm(forms.Form):

    QUALITY_CHOICES = [
        ('Like new','Like New'),
        ('Excellent','Excellent'),
        ('Light wear','Light wear'),
        ('Moderate wear','Moderate wear'),
        ('Heavy wear','Heavy wear'),
    ]

    title = forms.CharField(label = 'Title *', max_length=30)
    author = forms.CharField(label = 'Author *', max_length=30)
    quality = forms.ChoiceField(label = "Quality of book *", choices=QUALITY_CHOICES)
    price = forms.DecimalField(max_digits= 5, decimal_places=2, label="Price Offered *")
    course_dept = forms.CharField(label = 'Course Department', max_length=5, required=False)
    course_number = forms.IntegerField(label = 'Course Number', required=False)
    prof_last_name = forms.CharField(label = "Professor last name", max_length=30, required= False)
    
    image = forms.ImageField(required = False)

    #widgets
    title.widget.attrs.update({'class': 'form-control', 'placeholder': 'Wealth of Nations', 'style':'width:50%'} )
    author.widget.attrs.update({'class': 'form-control', 'placeholder': 'Adam Smith', 'style':'width:50%'} )
    course_dept.widget.attrs.update({'class': 'form-control', 'placeholder': 'ECON', 'style':'width:50%'} )
    course_number.widget.attrs.update({'class': 'form-control', 'placeholder': '2110', 'style':'width:50%'} )
    prof_last_name.widget.attrs.update({'class': 'form-control', 'placeholder': 'Santugini', 'style':'width:50%'} )
    quality.widget.attrs.update({'class': 'form-control', 'style':'width:50%'} )   
    price.widget.attrs.update({'class': 'form-control', 'placeholder': '25', 'style':'width:50%'} )
    image.widget.attrs.update({'class': 'form-control', 'style':'width:50%'} )

class SuggestionForm(forms.Form):
    name = forms.CharField(label = "Name (Optional)", required = False)
    suggestion = forms.CharField(widget = forms.Textarea, label = 'Suggestion')

    name.widget.attrs.update({'class': 'form-control', 'style':'width:30%'})
    suggestion.widget.attrs.update({'class': 'form-control', 'style':'height:100px'} )


