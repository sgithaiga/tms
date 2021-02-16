from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from .models import Fuel_mgt, Fuel_name, Fuel_price



class Fuel_mgtnewForm(forms.ModelForm):

    class Meta:
        model = Fuel_mgt
        fields = ('region', 'registration_no', 'fuel_type_requested',
                     'price_per_liter', 'fuel_amount_requested', 'total', 'driver_name', 'current_mileage')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price_per_liter'].queryset = Fuel_price.objects.none()

        if 'fuel_type_requested' in self.data:
            try:
                fuel_id = int(self.data.get('fuel_type_requested'))
                self.fields['price_per_liter'].queryset = Fuel_price.objects.filter(fuel_id=fuel_id).order_by('fuel_name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['price_per_liter'].queryset = self.instance.fuel_type_requested.price_per_liter_set.order_by('fuel_name')  
 