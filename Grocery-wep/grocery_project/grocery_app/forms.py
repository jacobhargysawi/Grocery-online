from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


from .models import Category



from .models import Supplier

from .models import Product

# ✅ General User Registration Form (Admin, Seller, Customer)
class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'role',
            'phone',
            'address',
        ]

# ✅ Strictly Customer Registration Form
class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "phone",
            "address",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "Customer"
        if commit:
            user.save()
        return user

# ✅ Form for Editing User in Admin Panel (safe and secure)
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'role',
            'phone',
            'address',
        ]






class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "description", "price", "cost", "stock_quantity",
            "category", "supplier", "image_url", "expiry_date"
        ]
        widgets = {
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }




class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]





class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_name", "contact_phone", "contact_email", "address"]




from django import forms
from .models import Shipment


from django import forms
from .models import Shipment

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ["order", "tracking_number", "carrier", "estimated_delivery_date", "status"]
        widgets = {
            "estimated_delivery_date": forms.DateInput(attrs={"type": "date"}),  # ✅ calendar picker
        }



from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']