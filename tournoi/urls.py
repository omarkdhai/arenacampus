from django.urls import path

from . import views

app_name = 'tournoi'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('jeu/ajouter/', views.jeu_ajouter, name='jeu_ajouter'),
    path('jeu/<int:pk>/', views.jeu_detail, name='jeu_detail'),
    path('equipes/', views.liste_equipes, name='liste_equipes'),
    path('equipe/ajouter/', views.equipe_ajouter, name='equipe_ajouter'),
    path('equipe/<int:pk>/modifier/', views.equipe_modifier, name='equipe_modifier'),
    path('equipe/<int:pk>/supprimer/', views.equipe_supprimer, name='equipe_supprimer'),
]
