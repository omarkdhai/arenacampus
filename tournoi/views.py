from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EquipeForm, JeuForm
from .models import Equipe, Jeu


def accueil(request):
    jeux = Jeu.objects.filter(actif=True).annotate(nb_equipes=Count('equipes'))
    return render(request, 'tournoi/accueil.html', {'jeux': jeux})


def jeu_detail(request, pk):
    jeu = get_object_or_404(Jeu, pk=pk)
    equipes = jeu.equipes.all()
    return render(request, 'tournoi/jeu_detail.html', {'jeu': jeu, 'equipes': equipes})


def liste_equipes(request):
    equipes = Equipe.objects.select_related('jeu')
    return render(request, 'tournoi/equipe_list.html', {'equipes': equipes})


def equipe_ajouter(request):
    if request.method == 'POST':
        form = EquipeForm(request.POST)
        if form.is_valid():
            equipe = form.save()
            messages.success(request, f"L'équipe « {equipe} » est inscrite au tournoi.")
            return redirect('tournoi:jeu_detail', pk=equipe.jeu.pk)
    else:
        # ?jeu=<pk> quand on vient de la page d'un jeu
        form = EquipeForm(initial={'jeu': request.GET.get('jeu')})
    return render(request, 'tournoi/equipe_form.html', {'form': form})


def equipe_modifier(request, pk):
    equipe = get_object_or_404(Equipe, pk=pk)
    if request.method == 'POST':
        form = EquipeForm(request.POST, instance=equipe)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'équipe « {equipe} » a été modifiée.")
            return redirect('tournoi:liste_equipes')
    else:
        form = EquipeForm(instance=equipe)
    return render(request, 'tournoi/equipe_form.html', {'form': form, 'equipe': equipe})


def equipe_supprimer(request, pk):
    equipe = get_object_or_404(Equipe, pk=pk)
    if request.method == 'POST':
        nom = equipe.nom_equipe
        equipe.delete()
        messages.success(request, f"L'équipe « {nom} » s'est désistée du tournoi.")
        return redirect('tournoi:liste_equipes')
    return render(request, 'tournoi/equipe_confirm_delete.html', {'equipe': equipe})


def jeu_ajouter(request):
    if request.method == 'POST':
        form = JeuForm(request.POST)
        if form.is_valid():
            jeu = form.save()
            messages.success(request, f"Le jeu « {jeu.nom} » a été ajouté.")
            return redirect('tournoi:jeu_detail', pk=jeu.pk)
    else:
        form = JeuForm()
    return render(request, 'tournoi/jeu_form.html', {'form': form})
