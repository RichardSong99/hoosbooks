from django.urls import path
from . import views
from django.contrib.staticfiles.urls import static, staticfiles_urlpatterns
from django.views.generic import TemplateView
# from django.contrib.auth.views import login, logout

urlpatterns = [
    path('', views.SearchView.as_view(), name='index'),
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout, name= 'logout'),
    path('register/',views.register, name = 'register'),
    path('search/', views.SearchView.as_view(), name = 'search'),
    path('<int:item_id>/order', views.OrderView.as_view() , name = 'order'),
    path('<int:item_id>/edit', views.edititem, name = 'edit'),
    path('<int:seller_id>/add', views.additem, name = 'add'),
    path('<int:item_id>/delete', views.deleteitem, name ='delete'),
    path('about/', views.about, name='about')
]

