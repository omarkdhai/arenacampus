from django.db import models


class Jeu(models.Model):
    PLATEFORME_CHOICES = [
        ('PC', 'PC'),
        ('Console', 'Console'),
        ('Mobile', 'Mobile'),
    ]

    nom = models.CharField("nom du jeu", max_length=100)
    plateforme = models.CharField(max_length=50, choices=PLATEFORME_CHOICES, default='PC')
    nombre_joueurs_equipe = models.PositiveIntegerField("joueurs par équipe", default=1)
    actif = models.BooleanField("ouvert au tournoi", default=True)

    class Meta:
        verbose_name = "jeu"
        verbose_name_plural = "jeux"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.plateforme})"


class Equipe(models.Model):
    nom_equipe = models.CharField("nom de l'équipe", max_length=100, unique=True)
    capitaine = models.CharField("capitaine (nom et prénom)", max_length=100)
    email_contact = models.EmailField("email de contact")
    jeu = models.ForeignKey(Jeu, on_delete=models.CASCADE, related_name='equipes')
    date_inscription = models.DateTimeField("date d'inscription", auto_now_add=True)

    class Meta:
        verbose_name = "équipe"
        verbose_name_plural = "équipes"
        ordering = ['-date_inscription']

    def __str__(self):
        return self.nom_equipe
