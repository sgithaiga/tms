from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from .models import Assign_fuel, Request_fuel, Vehicle_register, Driver, Fuel_mgt, Vehicle_issues, Vehicle_handover, station, Fuel_name, Fuel_price



APPROVAL_STATUS= [
    ('approved', 'Approved'),
    ('declined', 'Declined'),
    ]
class Assign_fuelForm(forms.ModelForm):

    class Meta:
        model = Assign_fuel
        fields = ('station_name', 'fuel_type', 'price_per_liter', 'liters_served', 
        	       'previous_liters_served', 'vehicle', 'current_mileage', 'amount', 'station')

class Request_fuelForm(forms.ModelForm):

    class Meta:
        model = Request_fuel
        fields = ('vehicle_registration_number', 'region', 'fuel_type_requested', 'price_per_liter',
                     'fuel_amount_requested', 'total', 'date_requested', 'driver_assigned')
    

class Vehicle_registerForm(forms.ModelForm):
    model = Vehicle_register
    fields = ('registration_no', 'region', 'make', 'engine_capacity', 'model', 'drive_type', 'transmission', 'body_type', 
                'fuel_tank_capacity', 'operational_status', 'mechanical_status', 'remarks')

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ('full_name', 'pf_no', 'gender', 'region_assigned', 'license_number', 'expiry_date', 'driver_history', 'assigned_vehicle')
        widgets = {
            'expiry_date': DatePickerInput(), # default date-format %m/%d/%Y will be used
        }

class requestSearchForm(forms.Form):
        search_text =  forms.CharField(
                    required = False,
                    label='Search for vehicle',
                    widget=forms.TextInput(attrs={'placeholder': 'search here!'})
                  )
        
        search_name = forms.CharField(
                    required = False,
                    label='Search name!',
                    widget=forms.TextInput(attrs={'placeholder': 'search here!'})
                  )

class Fuel_mgtreqForm(forms.Form):

    region = forms.ModelChoiceField(queryset=station.objects.all(), widget=forms.Select(attrs={'class': ''}))
    registration_no = forms.ModelChoiceField(queryset=Vehicle_register.objects.all(), widget=forms.Select(attrs={'class': ''}))
    fuel_type_requested = forms.ModelChoiceField(queryset=Fuel_name.objects.all(), widget=forms.Select(attrs={'class': ''}))
    price_per_liter = forms.ModelChoiceField(queryset=Fuel_price.objects.all(), widget=forms.Select(attrs={'class': ''}))
    fuel_amount_requested = forms.DecimalField(label="Enter fuel amount")
    total = forms.DecimalField(widget = forms.TextInput, label="Total")
    driver_name = forms.ModelChoiceField(queryset=Driver.objects.all(), widget=forms.Select(attrs={'class': ''}))
    current_mileage = forms.CharField(widget = forms.TextInput, label="Enter current mileage", max_length=50)


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
    
class Vehicle_issuesForm(forms.ModelForm):

    class Meta:
        model = Vehicle_issues
        fields = ('Vehicle_issue_topic', 'vehicle_registration_number', 'vehicle_issue')


class FormStepOne(forms.ModelForm):

    class Meta:
        model = Vehicle_handover
        fields = ('reason_for_handover', 'duty_station', 'registration_no', 'current_driver', 'assigned_driver')


class FormStepTwo(forms.ModelForm):

    class Meta:
        model = Vehicle_handover
        fields = ('head_lights', 'side_lights', 'rear_lights', 'mirrors_external', 'mirrors_internal', 'head_rests')

class FormStepThree(forms.ModelForm):

    class Meta:
        model = Vehicle_handover
        fields = ('wiper_arms', 'wiper_blades', 'sunvisors', 'radio', 'radio_knobs', 'speakers', 'radio_aerial', 'horn')

class FormStepFour(forms.ModelForm):

    class Meta:
        model = Vehicle_handover
        fields = ('spare_wheel', 'wheel_caps', 'wheel_spanner', 'floor_mats', 'tool_kit', 'jack', 'cigarette_lighter')

class FormStepFive(forms.ModelForm):

    class Meta:
        model = Vehicle_handover
        fields = ('vehicle_manual', 'life_savers', 'ignition_keys', 'door_keys', 'seat_belts', 'horn_relays', 'light_relays')

class FormStepSix(forms.ModelForm):

    class Meta:
        model = Vehicle_handover
        fields = ('head_rests', 'buffer_rubbers', 'petrol_tank_cap', 'key_holder', 'damage_on_departure', 'damage_on_arrival', 'cigarette_lighter')
