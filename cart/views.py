from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages


def cart_summary(request):
	# obtenemos el carrito
	cart = Cart(request)
	cart_products = cart.get_prods
	quantities = cart.get_quants
	totals = cart.cart_total()
	return render(request, "cart_summary.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals})




def cart_add(request):
	# obtenemos el carrito
	cart = Cart(request)
	# condicional para evaluar solicitud
	if request.POST.get('action') == 'post':
		# obtenemos id y cantidad de producto
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))

		# se busca producto en DB
		product = get_object_or_404(Product, id=product_id)
		
		# guardamos en sesión (ver funcion add en clase correspondiente)
		cart.add(product=product, quantity=product_qty)

		# obtenemos cantidad
		cart_quantity = cart.__len__()

		# retornamos response
		response = JsonResponse({'qty': cart_quantity})
		messages.success(request, ("Producto añadido a carrito..."))
		return response

def cart_delete(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# obtenemos id de producto
		product_id = int(request.POST.get('product_id'))
		# llamamos funcion borrar
		cart.delete(product=product_id)

		response = JsonResponse({'product':product_id})
		messages.success(request, ("Producto quitado de carrito."))
		return response


def cart_update(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# Obtenemos id y cantidad
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))

		cart.update(product=product_id, quantity=product_qty)

		response = JsonResponse({'qty':product_qty})
		messages.success(request, ("Carrito actualizado."))
		return response
