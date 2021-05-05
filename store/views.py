from . utils import cartData, cookieCart, guestOrder
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import UserRegisterForm
from django.contrib import messages
from . models import *
import datetime
import json

# Register View
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created. You can login now')
            return redirect('login')
    else:
        form = UserRegisterForm(request.POST)

    return render(request, 'store/register.html', {'form' : form})

# Home page view
def index(request):
    # getting cartData from utils file to show
    # cart count in bag info
    data = cartData(request)
    cartItem = data['cartItem']
    # Getting all categories to display in navbar dropdown menu
    all_cats = Category.objects.all()
    # passing the above in context
    context = {'cartItem': cartItem, 'all_cats': all_cats}
    return render(request, 'store/index.html', context)

# Store page view
def store(request):
    data = cartData(request)
    cartItem = data['cartItem']
    # Getting all products to display on store page
    products = Product.objects.all()
    all_cats = Category.objects.all()

    context = {'products': products, 'cartItem': cartItem, 'all_cats': all_cats}
    return render(request, 'store/store.html', context)

# Category view
def category(request, id):
    data = cartData(request)
    cartItem = data['cartItem']
    # Getting single category by id
    categories = Category.objects.filter(pk=id)
    all_cats = Category.objects.all()

    context = {'cartItem': cartItem, 'categories': categories, 'all_cats': all_cats}
    return render(request, 'store/category.html', context)

# Cart page view
def cart(request):
    print(request.user.is_authenticated)
    data = cartData(request)
    cartItem = data['cartItem']
    # getting order and no. items from cartData
    order = data['order']
    items = data['items']
    all_cats = Category.objects.all()

    context = {'items': items, 'order':order, 'cartItem': cartItem, 'all_cats': all_cats}
    return render(request, 'store/cart.html', context)

# Checkout page view
def checkout(request):
    data = cartData(request)
    cartItem = data['cartItem']
    order = data['order']
    items = data['items']
    all_cats = Category.objects.all()

    context = {'items': items, 'order':order, 'cartItem': cartItem, 'all_cats': all_cats}
    return render(request, 'store/checkout.html', context)

# Cart update item view for guest user
def updateItem(request):
    # loading json data
    data = json.loads(request.body)
    # getting product id and the action from json
    productId = data['productId']
    action = data['action']

    print('Product id: ', productId)
    print('Action: ', action)

    # Creating customer
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity -1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

# Order processing view
def processOrder(request):
    # creating tansction_id
    transcation_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transcation_id = transcation_id
    if total == order.get_cart_total:
        order.complete = True
    order.save()

    # adding shipping data to database
    if order.shipping == True:
        Shipping.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
            )

    return JsonResponse('Payment complete', safe=False)

