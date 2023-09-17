
from decimal import Decimal
from store.models import Product


class Cart():

    def __init__(self, request):
        self.session = request.session

        # Returning user - obtain user existing session
        cart = self.session.get('session_key')
        # name anything in the get('anything')

        # New user - generate a new session
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        self.cart = cart

    def add(self, product, product_qty):
        product_id = str(product.id)

        # test
        # if product is already in the cart, all we want to change is the quantity
        if product_id in self.cart:
            self.cart[product_id]['qty'] = product_qty
        # if the product does not exist, we take the price and the qty to add in the cart
        else:
            self.cart[product_id] = {'price': str(
                product.price), 'qty': product_qty}

        # tell django that we want to modify the session
        self.session.modified = True

    # function to delete product from the cart
    def delete(self, product):
        product_id = str(product)

        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

    # function to update product in the cart
    def update(self, product, qty):
        product_id = str(product)
        product_quantity = qty

        # check if product is in the cart
        if product_id in self.cart:
            # we want to change the qty based on the product_quantity
            self.cart[product_id]['qty'] = product_quantity

        self.session.modified = True

    def __len__(self):
        return sum(item['qty'] for item in self.cart.values())

    def __iter__(self):
        # the product id is the cart keys
        all_product_id = self.cart.keys()

        # select the product in db that matches the product in the shopping cart
        products = Product.objects.filter(id__in=all_product_id)

        # copy instances of our session data
        # need to optimize
        # cart = self.cart.copy()

        # best practice
        import copy
        cart = copy.deepcopy(self.cart)

        # loop through the matching product in our db and then add additional data (add some info from db)
        for product in products:
            cart[str(product.id)]['product'] = product

        # define our price
        for item in cart.values():
            item['price'] = Decimal(item['price'])

            # total price/cost
            item['total'] = item['price'] * item['qty']

            # get total price
            yield item

    # function to get total price
    def get_total(self):

        return sum(Decimal(item['price']) * item['qty'] for item in self.cart.values())
