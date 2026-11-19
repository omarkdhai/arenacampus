from django.contrib import admin

from .models import Equipe, Jeu


class EquipeInline(admin.TabularInline):
    model = Equipe
    extra = 0
    fields = ('nom_equipe', 'capitaine', 'email_contact')


@admin.register(Jeu)
class JeuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'plateforme', 'nombre_joueurs_equipe', 'actif', 'nb_equipes')
    list_filter = ('plateforme', 'actif')
    search_fields = ('nom',)
    list_editable = ('actif',)
    inlines = [EquipeInline]

    @admin.display(description="Équipes inscrites")
    def nb_equipes(self, obj):
        return obj.equipes.count()


@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nom_equipe', 'capitaine', 'email_contact', 'jeu', 'date_inscription')
    list_filter = ('jeu', 'jeu__plateforme')
    search_fields = ('nom_equipe', 'capitaine')
    date_hierarchy = 'date_inscription'
    list_select_related = ('jeu',)
