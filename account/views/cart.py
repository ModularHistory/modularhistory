from django.conf import settings
from django import forms
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django_mako_plus.controller import view_function

from . import initialize_template_vars
from account import models as amod
from catalog import models as cmod
from CHF.customform import CustomForm
import datetime


@view_function
def process_request(request):
  """Shopping cart page"""
  template_vars = initialize_template_vars(request)

  items = []
  for item in request.shopping_cart.cart_items:
    corresponding_product = cmod.Product.objects.get(id=item.product_id)
    item.price = corresponding_product.price
    item.product = corresponding_product
    items.append(item)

  template_vars['items'] = items
  return request.dmp.render('cart.html', template_vars)


###################################################################
###   Deletes an item in the cart

@view_function
def remove(request):
  """Deletes an item in the cart, then reloads the shopping cart page"""
  # Get the product
  try:
    pid = int(request.dmp.urlparams[0])
  except ValueError:
    return HttpResponseRedirect('/catalog/cart/')

  # Remove the item from the cart
  request.shopping_cart.remove_item(pid)

  # Reload
  return HttpResponseRedirect('/catalog/cart/')


##################################################################
###    Shopping cart ajax

@view_function
def add(request):
  """Shows the Add Form.  This should be called via Ajax."""
  try:
    product = cmod.Product.objects.get(id=request.dmp.urlparams[0])
  except cmod.Product.DoesNotExist:
    return Http404()

  you_already_claimed_it = False  # Boolean for checking if an UniqueProduct is already in the user's cart

  form = AddForm(request, initial={ 'quantity': 1 }, extra={ 'product': product })
  if request.method == 'POST': # The form has been submitted
    print('>>>>>>> The request method is POST.')
    form = AddForm(request, request.POST, extra={ 'product': product })
    print('>>>>>>> The form variable was initialized using request, request.POST, extra={ "product": product }')
    print('>>>>>>> The product in the extra dictionary is '+str(form.extra["product"])+'')
    if form.is_valid():
      print('>>>>>>> form.is_valid() evaluates to True.')
      try:
        desired_quantity = form.cleaned_data.get('quantity')
        # Add the item to the shopping cart
        if desired_quantity:
          print('>>>>>>> Calling the add_item method with the following parameters: product=product, desired_quantity='+str(form.cleaned_data.get('quantity'))+'')
          request.shopping_cart.add_item(product, form.cleaned_data.get('quantity'))
        else:
          print('>>>>>>> Calling the add_item method with the following parameters: product=product')
          request.shopping_cart.add_item(product)

      except ValueError as e:
        # This would normally be done in the form clean_quantity method, but since we have to do the work
        # (of adding) in order to get the error message, we are putting the try/catch here
        # and then manually adding the error message to the form.
        form.add_error('quantity', str(e))
        print('>>>>>>> The following ValueError occurred and has been added as a form error to the "quantity" field:')
        print('>>>>>>> '+str(e)+'')
    else:
      print('>>>>>>> form.is_valid() evaluated to False.')
      if isinstance(product, cmod.UniqueProduct):
        print('>>>>>>> The product is an IndividualItem.')
        if product in request.shopping_cart.get_items():  # The form is invalid because the IndividualItem is already in the user's cart
          print('>>>>>>> The product is already in the shopping cart.')
          you_already_claimed_it = True
        elif product.status == 'sold':  # The IndividualItem has already been sold
          print('>>>>>>> The product has a status of "sold" so cannot be added to the cart.')
      else:
        print('>>>>>>> The product is NOT an UniqueProduct.')

  template_vars = {
    'you_already_claimed_it': you_already_claimed_it,
    'form': form,
    'product': product,
  }
  return request.dmp.render('cart.add.html', template_vars)

class AddForm(CustomForm):
  quantity = forms.IntegerField(label='Quantity', required=False, min_value=1, max_value=100, widget=forms.NumberInput)

  def clean_quantity(self):
    """Ensures we have enough of this product"""
    try:
      self.request.shopping_cart.check_availability(self.extra['product'], self.cleaned_data['quantity'])
    except ValueError as e:
      raise forms.ValidationError(str(e))
    return self.cleaned_data['quantity']
