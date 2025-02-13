from django.urls import path
from . import views
from .views import *

urlpatterns=[
 path('', views.home, name='home') ,
 path('solve/', views.solve_lp, name='solve_lp'),
 path('graph/', views.generate_graph, name='generate_graph'),
 path('solve_transportation/', views.solve_transportation, name='solve_transportation'),
]