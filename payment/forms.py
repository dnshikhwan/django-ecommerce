from django import forms

from .models import ShippingAddress


class ShippingForm(forms.ModelForm):

    # define our models
    class Meta:
        model = ShippingAddress

        # define our fields, refer our models
        fields = ['full_name', 'email', 'address1',
                  'address2', 'city', 'state', 'zipcode']

        # exclude fields
        exclude = ['user',]
