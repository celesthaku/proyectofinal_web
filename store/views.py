from django.shortcuts import render, redirect
from .models import Product, Category, Profile, OrderItem, Order
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import OrderCreateForm, SignUpForm
from django.db.models import Q
import json
from cart.cart import Cart
import requests
from django.http import JsonResponse, FileResponse, HttpResponse
import tempfile
import os
import datetime
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import VendedorSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


#ultimo cambio

class VendedorCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados

    def post(self, request):
        serializer = VendedorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Vendedor creado correctamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendedorListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = VendedorSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados


class VendedorUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = VendedorSerializer
    lookup_field = 'id'  # Usaremos el ID del usuario para editar/eliminar
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados



# Vista para listar y agregar productos
class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]  # 🔹 Permite archivos (imágenes)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados

    def create(self, request, *args, **kwargs):
        print("\n🔹 SOLICITUD RECIBIDA EN /api/productos/ 🔹")
        print("Datos recibidos en request.data:", request.data)
        print("Archivos recibidos en request.FILES:", request.FILES)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("Producto guardado correctamente")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Error en la validación:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Vista para obtener, actualizar y eliminar productos
class ProductUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'  # Buscar por ID del producto
    parser_classes = [MultiPartParser, FormParser]  # 🔹 Permite actualizar imágenes
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados

class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados

def search(request):
	# manera de preguntarse si llenaron el formulario correspondiente
	if request.method == "POST":
		searched = request.POST['searched']
		# consultamos al db por el producto buscado
		# notar icontains y Q que son elementos de Django para hacer búsquedas complejas
		searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
		# evitamos los valores nulos
		if not searched:
			messages.success(request, "El producto no existe. Inténtelo de nuevo.")
			return render(request, "search.html", {})
		else:
			return render(request, "search.html", {'searched':searched})
	else:
		return render(request, "search.html", {})


def category_summary(request):
	categories = Category.objects.all()
	return render(request, 'category_summary.html', {"categories":categories})

def category(request, foo):
	# reemplazamos guiones con espacios
	foo = foo.replace('-', ' ')
	# sacamos la categoria de la url
	try:
		# y buscamos la categoria
		category = Category.objects.get(name=foo)
		products = Product.objects.filter(category=category)
		return render(request, 'category.html', {'products':products, 'category':category})
	except:
		messages.success(request, ("Categoría inexistente"))
		return redirect('home')


def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			# loguear usuario luego de autenticar con la funcion integrada de django
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ("Nombre de usuario creado. Complete el siguiente formulario."))
			return redirect('home')
		else:
			messages.success(request, ("Hubo un problema al registrarse. Inténtelo otra vez."))
			return redirect('register')
	else:
		return render(request, 'register.html', {'form':form})

def product(request,pk):
	product = Product.objects.get(id=pk)
	return render(request, 'product.html', {'product':product})


def home(request):
	products = Product.objects.all()
	return render(request, 'home.html', {'products':products})


def about(request):
	return render(request, 'about.html', {})

def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)

			# recuperamos el carrito de compras guardado del usuario desde la base de datos.
			# Esto se hace utilizando con el modelo Profile y el campo old_cart.
			# El carrito de compras guardado se almacena como una cadena JSON en el campo old_cart.
			current_user = Profile.objects.get(user__id=request.user.id)
			saved_cart = current_user.old_cart
			# convertir string de db a dict
			if saved_cart:
				# convertir a diccionario con JSON
				converted_cart = json.loads(saved_cart)
				# añadimos el diccionario cargado a la sesion
				# obtenemos el carrito
				cart = Cart(request)
				# hacemos un loop del carrito y lo añadimos con la funcion db_add
				for key,value in converted_cart.items():
					cart.db_add(product=key, quantity=value)

			messages.success(request, ("Ha iniciado sesión."))
			return redirect('home')
		else:
			messages.success(request, ("Error. Inténtelo otra vez."))
			return redirect('login')

	else:
		return render(request, 'login.html', {})


def logout_user(request):
	logout(request)
	messages.success(request, ("Cerró sesión. Gracias por visitarnos."))
	return redirect('home')








def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()

            products = cart.get_prods()
            quantities = cart.get_quants()
            for product in products:
                quantity = quantities[str(product.id)]
                OrderItem.objects.create(order=order, product=product, price=product.price, quantity=quantity)
            detalle_productos = OrderItem.objects.filter(order=order)
            cart.clear_cart()
            numerodecomprobante = order.id
            nombre_cliente = order.first_name + ' ' + order.last_name
            crearpdf(nombre_cliente, detalle_productos, numerodecomprobante)
            return render(request, 'order_created.html', {'order': order, 'cart': cart})
        else:
            # Manejar el caso en que el formulario no sea válido
            return render(request, 'order_create.html', {'cart': cart, 'form': form})
    else:
        form = OrderCreateForm()
        return render(request, 'order_create.html', {'cart': cart, 'form': form})


def consultar_dni(request):
    if request.method == 'POST':
        dni = request.POST.get('dni', '')

        # Verificar la longitud del DNI
        if len(dni) != 8:
            return JsonResponse({'error': 'El DNI debe tener 8 caracteres'})
        # En caso se acaben los tokens
        api_url2 = f'https://dniruc.apisperu.com/api/v1/dni/{dni}?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InVuaWNvYXJ0dXJvQGdtYWlsLmNvbSJ9.o-7RTLTPKl_xFJVxb9Ba0dkPlEtM978Ga0d4Ghjjx_o'
        # Realizar la solicitud a la API
        api_url = f'https://dniruc.apisperu.com/api/v1/dni/{dni}?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InVuaWNvYXJ0dXJvQGhvdG1haWwuY29tIn0.CZEJrTyyxySkQWBAab4QRMsIuzssE5wPI6pZOl6ifLY'
        #api_url = f'https://api.apis.net.pe/v1/dni?numero={dni}'
        response = requests.get(api_url2)

        if response.status_code == 200:
            data = response.json()
            # Obtener el nombre y el apellido de la respuesta de la API
            first_name = data.get('nombres', '')
            last_name = data.get('apellidoPaterno', '') + ' ' + data.get('apellidoMaterno', '')

            # Devolver los datos obtenidos de la API como respuesta JSON
            return JsonResponse({'first_name': first_name, 'last_name': last_name})
        else:
            return JsonResponse({'error': 'Error al consultar la API de RENIEC'})

    return JsonResponse({'error': 'Método no permitido'})


def crearpdf(nombre_cliente, detalle_productos, numerodecomprobante):
    documento_pdf = []
    fec_hoy = datetime.date.today()
    hoy = fec_hoy.strftime("%d/%m/%Y")

    style_sheet = getSampleStyleSheet()
    img = Image("static/assets/furniture.jpg", 120, 80)

    documento_pdf.append(Spacer(0, 50))

    estilo_monto_total = ParagraphStyle('', fontSize=10, textColor='#000', rightIndent=0, alignment=TA_CENTER)
    estilo_encabezado_2 = ParagraphStyle('', fontSize=10, textColor='#000', alignment=TA_CENTER)
    estilo_encabezado_1 = ParagraphStyle('', fontSize=6, textColor='#000', alignment=TA_CENTER)
    estilo_texto = ParagraphStyle('', fontSize=8, alignment=0, spaceBefore=0, spaceAfter=0, textColor='#000',
                                   leftIndent=0)
    encabezado1 = [Paragraph("<b>Jr. San Martín de Porres # 108  / Cel.: +51 926 780 600</b><br/><b> "
                             + "Huánuco - Perú - E-mail: unicoarturo@hotmail.com</b>",
                             estilo_encabezado_1)]

    encabezado2a = [Paragraph("<b>COMPROBANTE N° " + str(numerodecomprobante) + "</b>", estilo_encabezado_2)]

    encabezado2b = [Paragraph("<b>Fecha:   " + str(hoy) + "</b>", estilo_encabezado_2)]

    t_encabezado = [[img, encabezado2a], [encabezado1, encabezado2b]]

    tabla_encabezado = Table(t_encabezado, 242.5)
    tabla_encabezado.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.transparent),
        ('ALIGNMENT', (0, 0), (0, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (0, 0), 13),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 13),
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 1), colors.transparent),
        ('BACKGROUND', (1, 1), (-1, 1), colors.transparent),
        ('VALIGN', (0, 1), (-1, 1), 'TOP')
    ]))
    documento_pdf.append(tabla_encabezado)

    documento_pdf.append(Spacer(0, -17.5))
    t_cliente = [[Paragraph('''<font size=8> <b> </b></font>''', style_sheet["BodyText"])],
                 [Paragraph('<font size=8> <b>Cliente: ' + nombre_cliente + '</b></font>', estilo_texto)]]

    tabla_cliente = Table(t_cliente, 485)
    tabla_cliente.setStyle(TableStyle([
        ('INNERGRID', (0, 1), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 1), (-1, -1), 0.25, colors.black),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white)
    ]))
    documento_pdf.append(tabla_cliente)

    productos_table = [[Paragraph('''<font size=9> <b> </b></font>''', style_sheet["BodyText"])],
                       [Paragraph('''<font size=9> <b> </b>Precio</font>''', estilo_texto,),
                        Paragraph('''<font size=9> <b> </b>Cantidad</font>''', estilo_texto),
                        Paragraph('''<font size=9> <b> </b>Producto</font>''', estilo_texto),
                        Paragraph('''<font size=9> <b> </b>Subtotal</font>''', estilo_texto)]]
    subtotal_list = []
    for detalle in detalle_productos:
        producto = detalle.product
        precio = detalle.price
        cantidad = detalle.quantity
        subtotal = cantidad * precio
        subtotal_list.append(subtotal)

        estilocantidad = " <font size=8>" + str(cantidad) + "</font>"
        estiloprecio = " <font size=8>" + str(precio) + "</font>"
        estiloproducto = " <font size=8>" + str(producto) + "</font>"
        estilosubtotal = " <font size=8>" + str(subtotal) + "</font>"
        estilo_texto1 = ParagraphStyle('', fontSize=8, alignment=TA_CENTER, spaceBefore=0, spaceAfter=0,
                                       textColor='#000',
                                       leftIndent=0)
        productos_table.append([Paragraph("<b>S/." + str(estiloprecio) + " </b>", estilo_texto),
                                Paragraph(estilocantidad, estilo_texto1),
                                Paragraph(estiloproducto, estilo_texto),
                                Paragraph("<b>S/." + str(estilosubtotal) + " </b>", estilo_texto)])

    tabla_productos = Table(productos_table, (85, 40, 300, 60))
    tabla_productos.setStyle(TableStyle([
        ('INNERGRID', (0, 1), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 1), (-1, -1), 0.25, colors.white),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white)
    ]))
    documento_pdf.append(tabla_productos)
    precio_total = sum(subtotal_list)

    monto_total = [[Paragraph('''<font size=8> <b> </b></font>''', style_sheet["BodyText"]),
                    Paragraph("", estilo_monto_total),
                    Paragraph("", estilo_monto_total),
                    Paragraph("<b>TOTAL: S/." + str(precio_total) + " </b>", estilo_monto_total)]]

    importe_final = Table(monto_total, (30, 20, 300, 150))
    importe_final.setStyle(TableStyle([
        ('BOX', (-1, -1), (-1, -1), 0.25, colors.lightgrey),
        ('BACKGROUND', (-1, -1), (-1, -1), colors.lightgrey)
    ]))
    documento_pdf.append(importe_final)

    documento_pdf.append(Spacer(0, 50))

    fecha_de_hoy = str(datetime.date.today().day) + "-" + str(datetime.date.today().month) + "-"\
                    + str(datetime.date.today().year)

    file_path = os.path.dirname(os.path.abspath(__file__)) + "/pdf/" + fecha_de_hoy

    print(file_path)
    if not os.path.exists(file_path):
        os.makedirs(file_path)


    hora_actual = datetime.datetime.now()
    hora_de_hoy = str(hora_actual.hour) + "-" + str(hora_actual.minute) + "-"\
        + str(hora_actual.second)
    doc = SimpleDocTemplate(file_path + "/comprobante " + str(nombre_cliente) + "_"
        + fecha_de_hoy + "_" + hora_de_hoy
        + ".pdf", pagesize=A4, rightMargin=14, leftMargin=14, topMargin=5, bottomMargin=18)
    doc.build(documento_pdf)




    with open(doc.filename, 'rb') as temp_pdf_file:
        response = HttpResponse(temp_pdf_file.read(), content_type='application/pdf')

    # Establecer los encabezados de respuesta
    response['Content-Disposition'] = 'inline; filename=comprobante.pdf'

    return response