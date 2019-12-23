from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Model
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class User(AbstractUser):
    # address = models.CharField(null=True, blank=True, max_length=100)
    # address2 = models.CharField(null=True, blank=True, max_length=40)
    # city = models.CharField(null=True, blank=True, max_length=20)
    # state = models.CharField(null=True, blank=True, max_length=2, choices=settings.STATES)
    # zip_code = models.CharField(null=True, blank=True, max_length=5)
    # BIRTH_YEAR_CHOICES = [ str(i) for i in range(datetime.date.today().year-70, datetime.date.today().year-7) ]
    # date_of_birth = models.DateField(null=True, blank=True)
    avatar = ProcessedImageField(
        null=True, blank=True,
        upload_to='accounts/profile_pictures/%Y/%m',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 70}
    )
    # email_subscription = models.NullBooleanField(default=None, choices=settings.EMAIL_SUBSCRIPTIONS)
    force_password_change = models.BooleanField('Prompt user to change password upon first login', default=False)
    locked = models.BooleanField('Lock the account', default=False)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        """Prints for debugging purposes"""
        return self.get_full_name()

    @classmethod
    def create(cls, username=None, first_name=None, last_name=None, gender=None):
        # if username is None:
        #     username = f'{first_name} {last_name}'
        user = cls()
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        print(f'>>> Created user: {user}')
        return user

    # @classmethod
    # def create_or_retrieve(cls, first_name, last_name, username=None, gender=None, weight=None):
    #     print('>>> Creating or retrieving the user %s %s...' % (first_name, last_name))
    #     if len(cls.objects.filter(username=username)) > 0:
    #         existing_user = User.objects.filter(username=username)[0]
    #         if first_name and last_name and (existing_user.first_name != first_name
    #                                          or existing_user.last_name != last_name):
    #             raise Exception(f'The name of the existing user having username "{username}" '
    #                             f'does not match the name provided.')
    #     if len(cls.objects.filter(first_name=first_name, last_name=last_name)) > 0:
    #         print(f'>>> An existing user having the name "{first_name} {last_name}" was identified. Retrieving...')
    #         user = cls.objects.filter(first_name=first_name).filter(last_name=last_name)[0]
    #     else:
    #         user = cls.create(first_name=first_name, last_name=last_name, username=username, gender=gender)
    #     return user

    def lock(self):
        self.locked = True
        self.save()

    def unlock(self):
        self.locked = False
        self.save()


# class Subscription(Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#         related_name='subscriptions'
#     )
#     email = models.EmailField(null=True, blank=True)
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.email
#
#     def process(self, email=None):
#         api = mailchimp.Mailchimp(settings.MAILCHIMP_API_KEY)
#         api.lists.subscribe(settings.MAILCHIMP_SUBSCRIBE_LIST_ID, {'email': self.email if email is None else email})


# ######################################################################
# ##     Sales
# class Sale(Model):
#     """A sale"""
#     customer = models.ForeignKey(User, related_name='orders', on_delete=PROTECT)
#     datetime = models.DateTimeField(null=True, blank=True)
#     shipping_name = models.CharField(null=True, blank=True, max_length=40)
#     shipping_address = models.TextField(null=True, blank=True)
#     shipping_address2 = models.TextField(null=True, blank=True)
#     shipping_city = models.TextField(null=True, blank=True)
#     shipping_state = models.TextField(null=True, blank=True)
#     shipping_zip_code = models.TextField(null=True, blank=True)
#     # shipping_date = models.DateTimeField(null=True, blank=True)
#     # tracking_number = models.TextField(null=True, blank=True)
#     subtotal = models.DecimalField(null=True, max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))]) # max number is 99,999.99
#     discount = models.DecimalField(null=True, max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
#     shipping = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
#     tax = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
#     total = models.DecimalField(null=True, max_digits=7, decimal_places=2)
#     transaction_id = models.CharField(null=True, blank=True, max_length=99)
#
#     def __str__(self):
#         """Prints for debugging purposes"""
#         return 'Sale: %s (%s)' % (self.customer.get_full_name(), self.total)
#
#     @classmethod
#     def record(cls, request, user, first_name, last_name, shipping_address, shipping_address2, shipping_city, shipping_state, shipping_zip_code, shipping=None, tax=None, items=None, charge=None, coupon_id=None, transaction_id=None):
#         """Creates a sale. This code might throw an Integrity error if something goes wrong with the sale."""
#         with transaction.atomic():
#             # Create the sale record
#             sale = cls()
#             sale.datetime = timezone.now()
#             sale.customer = user
#             sale.shipping_name = '%s %s' % (first_name, last_name)
#             sale.shipping_address = shipping_address
#             sale.shipping_address2 = shipping_address2
#             sale.shipping_city = shipping_city
#             sale.shipping_state = shipping_state
#             sale.shipping_zip_code = shipping_zip_code
#             sale.transaction_id = transaction_id
#             sale.save()
#
#             coupon = None
#             if coupon_id:
#                 coupon = Coupon.objects.get(id=coupon_id)
#                 CouponUse.objects.create(coupon=coupon, user=user, sale=sale)
#
#             subtotal = Decimal('0.00')
#             discountable_subtotal = Decimal('0.00')
#             print(">>> Processing items...")
#             for item in (items if items else Cart(request.session).items()):
#                 product = Product.objects.get(id=item.id)
#                 print(">>> Product: %s, name: %s, price: %s" % (product, product.name, product.price))
#                 saleitem = SaleItem()
#                 saleitem.sale = sale
#                 saleitem.product = product
#                 saleitem.name = product.name
#                 saleitem.description = product.description
#                 saleitem.price = product.price
#                 saleitem.quantity = item.desired_quantity if hasattr(item, 'desired_quantity') else 1
#                 saleitem.extended = (saleitem.price * saleitem.quantity) if hasattr(item, 'desired_quantity') else saleitem.price
#                 if isinstance(product, Donation):
#                     print(">>> This one's a donation!  Adding amount as price.")
#                     saleitem.price = Decimal(request.session.get('donation'))
#                     saleitem.name = '%s' % product
#                 saleitem.save()
#                 print(">>> SaleItem: %s, name: %s, price: %s" % (saleitem, saleitem.name, saleitem.price))
#                 # Update the product quantity and/or set the individual item status to 'sold'
#                 if isinstance(product, BulkProduct):
#                     product.quantity -= saleitem.quantity
#                 elif isinstance(product, UniqueProduct):
#                     product.status = 'sold'
#                 product.save()
#                 if not isinstance(product, Donation):
#                     discountable_subtotal += saleitem.price
#                 subtotal += saleitem.price
#
#             sale.subtotal = subtotal
#             discount = None
#             if coupon:
#                 discount = discountable_subtotal - (coupon.fraction * discountable_subtotal)
#                 total = subtotal
#
#             if charge is not None:
#                 charge = Decimal(charge)
#                 if subtotal > charge:
#                     sale.discount = subtotal - charge
#                     print('Discount: %s' % sale.discount)
#                     total = subtotal - sale.discount
#                     if discount != sale.discount:
#                         print(">>> Hmmmm... %s != %s" % (discount, sale.discount))
#
#             if shipping:
#                 sale.shipping = shipping
#                 total += shipping
#             if tax:
#                 sale.tax = tax
#                 total += tax
#
#             sale.total = charge if charge else total
#             sale.save()
#             print(">>> Finished recording sale: %s" % sale)
#
#         if transaction_id:
#             # Payment
#             payment = Payment()
#             payment.sale = sale
#             payment.user = user
#             payment.datetime = timezone.now()
#             payment.amount = sale.total
#             payment.validation_code = 'Unvalidated'
#             payment.save()
#             print(">>> Finished recording payment: %s" % payment)
#
#         # Return
#         return sale
#
#
# class SaleItem(Model):
#     """A line item on a sale"""
#     sale = models.ForeignKey(Sale, related_name="items", on_delete=CASCADE)
#     product = models.ForeignKey("catalog.Product", null=True, related_name='sale_items', on_delete=PROTECT)
#     name = models.CharField(null=True, blank=True, max_length=80)
#     description = models.TextField(null=True, blank=True)
#     price = models.DecimalField(blank=True, null=True, max_digits=7, decimal_places=2) # max number is 99,999.99
#     quantity = models.IntegerField(blank=True, null=True)
#     extended = models.DecimalField(blank=True, null=True, max_digits=7, decimal_places=2) # max number is 99,999.99
#     _return = models.ForeignKey("account.Return", null=True, related_name='items', on_delete=PROTECT)
#
#     def __str__(self):
#         """Prints for debugging purposes"""
#         return '%s' % (self.product.name)
#
#
# class Coupon(Model):
#     """A payment on a sale"""
#     name = models.CharField(null=True, blank=True, max_length=40)
#     code = models.CharField(max_length=16, unique=True)
#     description = models.TextField(null=True, blank=True)
#     fraction = models.DecimalField(null=True, max_digits=5, decimal_places=4, validators=[MinValueValidator(Decimal('0.0000')), MaxValueValidator(Decimal('1.0000'))])
#     quantity_available = models.IntegerField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#
#     def __str__(self):
#         """Prints for debugging purposes"""
#         return '%s: %s' % (self.name, self.fraction)
#
#     def is_available(self):
#         is_available = True
#         if self.quantity_available is not None and self.quantity_available < 1:
#             is_available = False
#         elif not self.is_active:
#             is_available = False
#         return is_available
#
#
# class CouponUse(Model):
#     """A use of a coupon"""
#     coupon = models.ForeignKey(Coupon, related_name="uses", on_delete=PROTECT)
#     user = models.ForeignKey(User, related_name="coupons_used", on_delete=CASCADE)
#     sale = models.ForeignKey(Sale, null=True, related_name="coupons_used", on_delete=CASCADE)
#
#     def __str__(self):
#         """Prints for debugging purposes"""
#         return '%s: %s' % (self.user, self.coupon)
#
#
# class Payment(Model):
#     """A payment on a sale"""
#     user = models.ForeignKey(User, on_delete=PROTECT)
#     sale = models.ForeignKey(Sale, null=True, related_name="payments", on_delete=PROTECT)
#     amount = models.DecimalField(blank=True, null=True, max_digits=7, decimal_places=2) # max number is 99,999.99
#     tender_id = models.CharField(blank=True, max_length=99)
#     datetime = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         """Prints for debugging purposes"""
#         return 'Payment: %s (%s)' % (self.datetime, self.amount)
#
#
# class Return(Model):
#     """A payment on a sale"""
#     user = models.ForeignKey(User, on_delete=PROTECT)
#     sale = models.ForeignKey(Sale, null=True, related_name="returns", on_delete=PROTECT)
#     amount = models.DecimalField(blank=True, null=True, max_digits=7, decimal_places=2) # max number is 99,999.99
#     datetime = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         """Prints for debugging purposes"""
#         return 'Return: %s (Refunded amount: %s)' % (self.sale, self.amount)
#
#     @classmethod
#     def record(cls, user=None, sale=None, amount=None, items=None):
#         r = cls.objects.create(user=user, sale=sale, amount=amount)
#         if items:
#             for item in items:
#                 item._return = r
#                 item.save()
#         return r
