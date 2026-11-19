from django import forms

from .models import Equipe, Jeu


class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = ['nom_equipe', 'capitaine', 'email_contact', 'jeu']
        widgets = {
            'nom_equipe': forms.TextInput(attrs={'placeholder': 'Ex : Les Dragons RSI'}),
            'capitaine': forms.TextInput(attrs={'placeholder': 'Nom et prénom'}),
            'email_contact': forms.EmailInput(attrs={'placeholder': 'capitaine@exemple.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # seulement les jeux actifs (+ le jeu actuel si on modifie)
        jeux = Jeu.objects.filter(actif=True)
        if self.instance.pk:
            jeux = jeux | Jeu.objects.filter(pk=self.instance.jeu_id)
        self.fields['jeu'].queryset = jeux.distinct()
        self.fields['jeu'].empty_label = "— Choisir un jeu —"

    def clean_nom_equipe(self):
        nom = self.cleaned_data['nom_equipe'].strip()
        if Equipe.objects.filter(nom_equipe__iexact=nom).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Une équipe porte déjà ce nom.")
        return nom

    def clean_capitaine(self):
        capitaine = " ".join(self.cleaned_data['capitaine'].split())
        if len(capitaine.split()) < 2:
            raise forms.ValidationError("Indiquez le nom et le prénom du capitaine.")
        return capitaine


class JeuForm(forms.ModelForm):
    class Meta:
        model = Jeu
        fields = ['nom', 'plateforme', 'nombre_joueurs_equipe', 'actif']
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Ex : Valorant'}),
            'nombre_joueurs_equipe': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_nom(self):
        return self.cleaned_data['nom'].strip()

    def clean_nombre_joueurs_equipe(self):
        nombre = self.cleaned_data['nombre_joueurs_equipe']
        if nombre < 1:
            raise forms.ValidationError("Une équipe doit compter au moins 1 joueur.")
        return nombre
