from django.urls import path
from . import views

urlpatterns = [
    path('menschen/', views.menschen, name='menschen'),
    path('grammar/', views.grammar, name='grammar'),
    path('practice-materials/', views.grammar, name='practice-materials'),
    path('download-center/', views.books_view, name='download-center'),

]