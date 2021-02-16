from django.http import HttpResponse

def load_prices(request):
    fuel_id = request.GET.get('fuel_type_requested')
    prices = Fuel_price.objects.filter(fuel_id=fuel_id).all()
    return render(request, 'transport/prices_dropdown_list_options.html', {'prices': prices})
 



class Fuel_mgtCreateView(CreateView):
    model = Fuel_mgt
    form_class = Fuel_mgtnewForm    