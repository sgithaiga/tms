from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa
from bootstrap_datepicker_plus import DatePickerInput
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from formtools.wizard.views import SessionWizardView

from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView,
                                  TemplateView)

from .models import Vehicle_register, Driver, Request_fuel, Assign_fuel, Fuel_mgt, Vehicle_issues, Vehicle_handover, Fuel_price, Fuel_name
from transport.forms import Assign_fuelForm, Request_fuelForm, Vehicle_registerForm, requestSearchForm, Fuel_mgtreqForm, FormStepOne, FormStepTwo, FormStepThree, FormStepFour, FormStepFive, FormStepSix, Fuel_mgtnewForm

from search_views.search import SearchListView
from search_views.filters import BaseFilter

from .filters import RequestFilter

# Create your views here.

@login_required       
def home_view(request):
    return render(request, 'transport/transport-home.html')

def load_prices(request):
    fuel_id = request.GET.get('fuel_type_requested')
    prices = Fuel_price.objects.filter(fuel_id=fuel_id).all()
    return render(request, 'transport/prices_dropdown_list_options.html', {'prices': prices})
     # return JsonResponse(list(cities.values('id', 'name')), safe=False)

def fuelapproval_render_pdf_view(request, *args, **kwargs):
    pk = kwargs.get('pk')
    approval = get_object_or_404(Request_fuel, pk=pk)

    template_path = 'transport/transport_pdf.html'
    context = {'approval': approval}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Fuel Approval.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response



class UserAccessMixin(PermissionRequiredMixin):

    #check if user is logged in
    def dispatch(self, request, *args, **kwargs):
        if (not self.request.user.is_authenticated):
            return redirect_to_login(self.request.get_full_path,
                                    self.get_login_url(), self.get_redirect_field_name())
        #check if user has permissions
        if not self.has_permission():
            return redirect('/error/')
        return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)

class PermissionsView(TemplateView):
    template_name = "transport/permissions_error.html"

def index(request):  
    req = Fuel_mgtreqForm()  
    return render(request, 'transport/index.html', {'form':req})  

class Request_fuelCreateView(LoginRequiredMixin, UserAccessMixin, CreateView):

    permission_required = 'transport.add_request_fuel'

    model = Request_fuel
    fields = ['vehicle_registration_number', 'region', 'fuel_type_requested', 'fuel_amount_requested', 'price_per_liter', 'total', 'driver_assigned']

    def form_valid(self,form):
        form.instance.requested_by = self.request.user
        return super().form_valid(form)

class Request_fueltDetailView(LoginRequiredMixin, DetailView):

    
    
    model = Request_fuel
    template_name = 'transport/Request_fuel_detail.html' #<app>/<model>_<viewtype>.html

class Request_fuelListView(LoginRequiredMixin, ListView):

    model = Request_fuel
    template_name = 'transport/Request_fuel_list.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_requested']
    paginate_by = 10

#display user requests in class list view
class UserRequest_fuelListView(LoginRequiredMixin, ListView):

    model = Request_fuel
    template_name = 'transport/Request_fuel_list_userfrm.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Request_fuel.objects.filter(requested_by=user).order_by('-date_requested')

class Request_fuel_UpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    #permission_required = ('transport.view_request_fuel', 'transport.change_request_fuel')
    model = Request_fuel
    fields = ['vehicle_registration_number', 'region', 'fuel_type_requested', 'fuel_amount_requested', 'price_per_liter', 'total']

    def form_valid(self,form):
        form.instance.requested_by = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.requested_by:
            return True
        return False

class Request_fuelDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Request_fuel
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.requested_by:
            return True
        return False

class Request_fuelUpdate(LoginRequiredMixin, UserAccessMixin, UpdateView):

    permission_required = ('transport.view_request_fuel', 'transport.change_request_fuel')
    model = Request_fuel
    template_name = 'transport/Request_fuel_approve.html' #<app>/<model>_<viewtype>.html
    fields = ['approved', 'declined', 'reason']

    def form_valid(self,form):
        form.instance.approved_by = self.request.user
        return super().form_valid(form)

class Request_fuel_declineUpdate(LoginRequiredMixin, UserAccessMixin, UpdateView):

    permission_required = ('transport.view_request_fuel', 'transport.change_request_fuel')
    model = Request_fuel
    template_name = 'transport/Request_fuel_decline.html' #<app>/<model>_<viewtype>.html
    fields = ['declined', 'reason']

    def form_valid(self,form):
        form.instance.approved_by = self.request.user
        return super().form_valid(form)


class Request_fuel_completeUpdate(LoginRequiredMixin, UserAccessMixin, UpdateView):

    permission_required = 'transport.change_request_fuel'
    model = Request_fuel
    template_name = 'transport/Request_fuel_complete.html' #<app>/<model>_<viewtype>.html
    fields = ['fuel_issue_complete']

class Assign_fuelCreateView(LoginRequiredMixin, UserAccessMixin, CreateView):

    permission_required = 'transport.add_assign_fuel'
    model = Assign_fuel
    fields = ['station_name', 'fuel_type', 'price_per_liter', 'liters_served', 'vehicle', 'current_mileage', 'amount', 'station']

    def form_valid(self,form):
        form.instance.entered_by = self.request.user
        return super().form_valid(form)


class Assign_fuelListView(LoginRequiredMixin, ListView):
    model = Assign_fuel
    template_name = 'transport/Assign_fuel_list.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 10

class Assign_fueltDetailView(LoginRequiredMixin, DetailView):
    model = Assign_fuel
    template_name = 'transport/Assign_fuel_detail.html' #<app>/<model>_<viewtype>.html

class DriverListView(LoginRequiredMixin, ListView):
    model = Driver
    template_name = 'transport/Driver_list.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 10

class DriverDetailView(LoginRequiredMixin, DetailView):
    model = Driver
    template_name = 'transport/Driver_detail.html' #<app>/<model>_<viewtype>.html

class Vehicle_registerListView(LoginRequiredMixin, ListView):
    model = Vehicle_register
    template_name = 'transport/Vehicle_register_list.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 10

class Vehicle_registerDetailView(LoginRequiredMixin, DetailView):
    model = Vehicle_register
    template_name = 'transport/Vehicle_register_detail.html' #<app>/<model>_<viewtype>.html

class Vehicle_registerCreateView(LoginRequiredMixin, UserAccessMixin, CreateView):

    permission_required = 'transport.add_vehicle_register'
    model = Vehicle_register
    template_name = 'transport/Vehicle_register_form.html' #<app>/<model>_<viewtype>.html

    fields = ['registration_no', 'region', 'make', 'engine_capacity', 'model', 'drive_type', 'transmission', 'body_type', 'fuel_tank_capacity', 'operational_status', 
                'mechanical_status', 'remarks']

    def form_valid(self,form):
        form.instance.registered_by = self.request.user
        return super().form_valid(form)

class DriverCreateView(LoginRequiredMixin, UserAccessMixin, CreateView):
    permission_required = 'transport.add_driver'
    model = Driver
    fields = ['full_name', 'pf_no', 'gender', 'region_assigned', 'license_number', 'expiry_date', 'driver_history', 'assigned_vehicle']
    
    def get_form(self):
        form = super().get_form()
        form.fields['expiry_date'].widget = DatePickerInput()
        return form
    def form_valid(self,form):
        form.instance.entered_by = self.request.user
        return super().form_valid(form)

class RequestFilter(BaseFilter):
    search_fields = {
        
        'search_vehicle_registration_number_exact' : { 'operator' : '__exact', 'fields' : ['vehicle_registration_number'] },

    }

class RequestSearchList(SearchListView):
    model = Request_fuel
    paginate_by = 10
    template_name = "transport/search.html"
    form_class = requestSearchForm
    filter_class = RequestFilter

def search(request):
    rq_list = Request_fuel.objects.all()
    rq_filter = RequestFilter(request.GET, queryset=rq_list)
    return render(request, 'transport/search.html', {'filter': rq_filter})

class Vehicle_issuesCreateView(LoginRequiredMixin, UserAccessMixin, CreateView):
    
    permission_required = 'transport.add_vehicle_issues'

    model = Vehicle_issues
    fields = ['Vehicle_issue_topic', 'vehicle_registration_number', 'vehicle_issue']

    def form_valid(self,form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class Vehicle_issuesListView(LoginRequiredMixin, ListView):
    model = Vehicle_issues
    template_name = 'transport/Vehicle_issues_list.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_created']
    paginate_by = 10

class FormWizardView(SessionWizardView):
    model = Vehicle_handover
    template_name = "transport/vehicle_handover.html"
    form_list = [FormStepOne, FormStepTwo, FormStepThree, FormStepFour, FormStepFive, FormStepSix]

    def done(self, form_list, **kwargs):
        return render(self.request, 'transport/vehicle_handover_done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })


class Fuel_mgtCreateView(CreateView):
    model = Fuel_mgt
    form_class = Fuel_mgtnewForm    