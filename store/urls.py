from django.urls import path
from . import views
from .views import (VendedorListCreateView, VendedorUpdateDeleteView, ProductListCreateView, ProductUpdateDeleteView,
                    CategoryListView)

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('product/<int:pk>', views.product, name='product'),
    path('category/<str:foo>', views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),
    path('search/', views.search, name='search'),
    path('order_create/', views.order_create, name='order_create'),
    path('consultar_dni/', views.consultar_dni, name='consultar_dni'),
    path('api/vendedores/', VendedorListCreateView.as_view(), name='listar_agregar_vendedor'),
    path('api/vendedores/<int:id>/', VendedorUpdateDeleteView.as_view(), name='editar_eliminar_vendedor'),
    path('api/productos/', ProductListCreateView.as_view(), name='listar_agregar_producto'),
    path('api/productos/<int:id>/', ProductUpdateDeleteView.as_view(), name='editar_eliminar_producto'),
    path('api/categorias/', CategoryListView.as_view(), name='listar_categorias'),
]
