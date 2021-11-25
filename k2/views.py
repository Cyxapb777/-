from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from django.views.generic import ListView
from .models import *
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import DetailView
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from el_pagination.views import AjaxListView
from el_pagination.decorators import page_template


class CustomerView(ListView):
    model = Customer
    template_name = 'customer_list.html'


# форма регистрации
class RegistrationForm(forms.Form):
    username = forms.CharField(min_length=5, label='Логин')
    password = forms.CharField(min_length=8, widget=forms.PasswordInput, label='Пароль')
    password2 = forms.CharField(min_length=8, widget=forms.PasswordInput, label='Повторите ввод')
    email = forms.EmailField(label='Email')
    last_name = forms.CharField(label='Фамилия')
    first_name = forms.CharField(label='Имя')


class ComputerForm(forms.ModelForm):
    class Meta(object):
        model = Computer
        fields = ['name', 'price', 'pic', 'description', 'quantity', 'type']

    def save(self):
        computer = Computer()
        computer.name = self.cleaned_data.get('name')
        computer.price = self.cleaned_data.get('price')
        computer.type = self.cleaned_data.get('type')
        computer.quantity = self.cleaned_data.get('quantity')
        computer.description = self.cleaned_data.get('description')
        f = self.cleaned_data.get('pic')
        computer.pic = f
        computer.save()


class AuthorizationForm(forms.Form):
    username = forms.CharField(label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


# регистрация
def add(request):
    if request.method == 'POST':

        name1 = request.POST.get('name')
        price1 = request.POST.get('price')
        type1 = request.POST.get('type')
        quantity1 = request.POST.get('quantity')
        description1 = request.POST.get('description')
        pic1 = request.FILES.get('pic')
        print(type(price1))
        try:
            int(price1)
            int(quantity1)
        except:
            return render(request, 'add.html', {'error': "Неверно введена цена или количество"})

        else:
            comp = Computer(name=name1, price=price1, type=type1, quantity=quantity1, description=description1,
                            pic=pic1)
            comp.save()
        return HttpResponseRedirect('/item-' + name1)
    return render(request, 'add.html', locals())


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        is_val = form.is_valid()
        data = form.cleaned_data
        if data['password'] != data['password2']:
            is_val = False
            form.add_error('password2', ['Пароли должны совпадать'])
        if User.objects.filter(username=data['username']).exists():
            form.add_error('username', ['Такой логин уже занят'])
            is_val = False

        if is_val:
            data = form.cleaned_data
            user = User.objects.create_user(data['username'], data['email'], data['password'])
            print(user)
            cust = Customer()
            cust.user = user
            cust.first_name = data['first_name']
            cust.last_name = data['last_name']
            cust.save()
            return HttpResponseRedirect('/authorization/')
    else:
        form = RegistrationForm()

    return render(request, 'registration.html', {'form': form})


# авторизация django
def authorization(request):
    if request.method == 'POST':
        form = AuthorizationForm(request.POST)
        print(form)
        data = form.cleaned_data
        if form.is_valid():
            user = authenticate(request, username=data['username'], password=data['password'])
            # user = authenticate(request, username='petrov',password='12345678')
            print(len(data['username']), len(data['password']))
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/success_authorization')
            else:
                form.add_error('username', ['Неверный логин или пароль'])
                # raise forms.ValidationError('Имя пользователя и пароль не подходят')
    else:
        form = AuthorizationForm()
    return render(request, 'authorization.html', {'form': form})


# успешная авторизация django
@login_required(login_url='/authorization')
def success_authorization(request):
    return HttpResponseRedirect('/')


# class ItemsView(AjaxListView):
#     template_name = 'labApp/templates/list.html'
#     context_object_name = "list_object"
#     page_template = 'labApp/templates/list_object.html'
@page_template('list_object.html')
def ItemsView(request, template='list.html', extra_context=None):
    dict_customers = {}  # код компа - массив покупателей
    data = Computer.objects.all()
    form = ComputerForm()
    for c in data:  # по компам
        customers = []  # купили
        orders = Order.objects.all()
        for o in orders:  # по заказам
            cur_cust = o.customer.first_name
            # print(cur_cust)# покупатель, сделавший заказ
            for item in o.items.all():  # по элементам заказа
                if item.name == c.name:  # если текущий комп
                    if cur_cust not in customers:
                        customers.append(cur_cust)  # покупателя в купили
        dict_customers[c.name] = customers  # список покупателей для компа
    return render(request, template,
                  context={'search': data,
                           'customers': dict_customers,

                           'form': form
                           })


class OneItem(DetailView):
    model = Computer
    context_object_name = 'computer'
    template_name = 'object.html'

    def get_context_data(self, **kwargs):
        context = super(OneItem, self).get_context_data(**kwargs)
        dict_customers = {}  # код компа - массив покупателей
        data = Computer.objects.all()

        for c in data:  # по компам
            customers = []  # купили
            orders = Order.objects.all()
            for o in orders:  # по заказам
                cur_cust = o.customer.first_name
                # покупатель, сделавший заказ
                for item in o.items.all():
                    # по элементам заказа
                    # print(c.name)
                    if item.name == c.name:  # если текущий комп
                        if cur_cust not in customers:
                            customers.append(cur_cust)  # покупателя в купили
            dict_customers[c.name] = customers
            # print(dict_customers)
        context['customers'] = dict_customers
        # print(context)
        return context


def ord(request, namekomp):
    if request.method == "GET":
        comp = Computer.objects.get(name=namekomp)
        id = request.user.id - 1
        cust = Customer.objects.get(id=id)
        price = 1
        order = Order()
        order.customer = cust
        order.price = price
        order.total = 1
        order.save()
        order2 = BelongTO()
        order2.quantity = 1
        order2.id = id
        order2.item_id = comp
        order2.order_id = id
        order2.save()
        return HttpResponseRedirect('/orders/')


class OrdersView(View):
    def get(self, request):
        empty_orders = []
        computers_in_order = BelongTO.objects.all()  # код заказа - компы
        prices = {}  # цены
        data = Order.objects.filter(
            customer_id=request.user.id - 1).all()  # заказы пользователя
        for o in data:
            computers = BelongTO.objects.filter(
                order_id=o.code).all()  # компьютеры заказа
            if len(computers) == 0:
                empty_orders.append(o.code)
            total = 0
            for c in computers:
                cur_comp = Computer.objects.get(name=c.item_id)
                if c.item_id not in prices.keys():
                    prices[c.item_id] = cur_comp.price
                total = total + cur_comp.price * c.quantity
            o.total = total
            o.save()

        return render(request, 'orders.html',
                      context={"data": data,
                               "computers": computers_in_order,
                               "prices": prices,
                               'empty_orders': empty_orders})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
