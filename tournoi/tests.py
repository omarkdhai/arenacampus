from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .forms import EquipeForm
from .models import Equipe, Jeu


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.valorant = Jeu.objects.create(nom="Valorant", plateforme="PC", nombre_joueurs_equipe=5)
        cls.fifa = Jeu.objects.create(nom="FIFA", plateforme="Console", nombre_joueurs_equipe=1)
        cls.ferme = Jeu.objects.create(nom="Jeu fermé", plateforme="Mobile", actif=False)
        cls.equipe = Equipe.objects.create(
            nom_equipe="Les Dragons", capitaine="Ben Ali Sami",
            email_contact="sami@exemple.com", jeu=cls.valorant,
        )



class ModelesTests(BaseTestCase):

    def test_valeurs_par_defaut_jeu(self):
        jeu = Jeu.objects.create(nom="Chess", plateforme="PC")
        self.assertEqual(jeu.nombre_joueurs_equipe, 1)
        self.assertTrue(jeu.actif)

    def test_str(self):
        self.assertEqual(str(self.valorant), "Valorant (PC)")
        self.assertEqual(str(self.equipe), "Les Dragons")

    def test_date_inscription_automatique(self):
        self.assertIsNotNone(self.equipe.date_inscription)

    def test_nom_equipe_unique(self):
        with self.assertRaises(IntegrityError):
            Equipe.objects.create(nom_equipe="Les Dragons", capitaine="X Y",
                                  email_contact="x@y.com", jeu=self.fifa)

    def test_suppression_en_cascade(self):
        self.valorant.delete()
        self.assertFalse(Equipe.objects.filter(nom_equipe="Les Dragons").exists())

    def test_related_name(self):
        self.assertIn(self.equipe, self.valorant.equipes.all())



class VuesLectureTests(BaseTestCase):

    def test_accueil_affiche_seulement_jeux_actifs(self):
        response = self.client.get(reverse('tournoi:accueil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournoi/accueil.html')
        self.assertTemplateUsed(response, 'tournoi/base.html')
        self.assertContains(response, "Valorant")
        self.assertNotContains(response, "Jeu fermé")

    def test_detail_jeu(self):
        response = self.client.get(reverse('tournoi:jeu_detail', args=[self.valorant.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Les Dragons")

    def test_detail_jeu_sans_equipe(self):
        response = self.client.get(reverse('tournoi:jeu_detail', args=[self.fifa.pk]))
        self.assertContains(response, "Aucune équipe")

    def test_detail_jeu_inexistant_404(self):
        response = self.client.get(reverse('tournoi:jeu_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_liste_equipes(self):
        response = self.client.get(reverse('tournoi:liste_equipes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Les Dragons")
        self.assertContains(response, "Valorant")



class FormulaireEquipeTests(BaseTestCase):

    def donnees(self, **kwargs):
        data = {'nom_equipe': "Team Phoenix", 'capitaine': "Trabelsi Amine",
                'email_contact': "amine@exemple.com", 'jeu': self.fifa.pk}
        data.update(kwargs)
        return data

    def test_formulaire_valide(self):
        self.assertTrue(EquipeForm(data=self.donnees()).is_valid())

    def test_email_invalide(self):
        form = EquipeForm(data=self.donnees(email_contact="pas-un-email"))
        self.assertFalse(form.is_valid())
        self.assertIn('email_contact', form.errors)

    def test_nom_duplique_insensible_a_la_casse(self):
        form = EquipeForm(data=self.donnees(nom_equipe="les dragons"))
        self.assertFalse(form.is_valid())
        self.assertIn('nom_equipe', form.errors)

    def test_capitaine_nom_et_prenom(self):
        form = EquipeForm(data=self.donnees(capitaine="Amine"))
        self.assertFalse(form.is_valid())
        self.assertIn('capitaine', form.errors)

    def test_jeu_ferme_refuse(self):
        form = EquipeForm(data=self.donnees(jeu=self.ferme.pk))
        self.assertFalse(form.is_valid())
        self.assertIn('jeu', form.errors)


class CrudEquipeTests(BaseTestCase):

    def test_ajouter_get(self):
        response = self.client.get(reverse('tournoi:equipe_ajouter'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_ajouter_post_valide(self):
        response = self.client.post(reverse('tournoi:equipe_ajouter'), {
            'nom_equipe': "Team Phoenix", 'capitaine': "Trabelsi Amine",
            'email_contact': "amine@exemple.com", 'jeu': self.fifa.pk,
        })
        self.assertRedirects(response, reverse('tournoi:jeu_detail', args=[self.fifa.pk]))
        self.assertTrue(Equipe.objects.filter(nom_equipe="Team Phoenix").exists())

    def test_ajouter_post_invalide(self):
        response = self.client.post(reverse('tournoi:equipe_ajouter'), {'nom_equipe': ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Equipe.objects.count(), 1)

    def test_modifier_get_pre_rempli(self):
        response = self.client.get(reverse('tournoi:equipe_modifier', args=[self.equipe.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Les Dragons"')

    def test_modifier_post(self):
        response = self.client.post(reverse('tournoi:equipe_modifier', args=[self.equipe.pk]), {
            'nom_equipe': "Les Dragons", 'capitaine': "Nouveau Capitaine",
            'email_contact': "nouveau@exemple.com", 'jeu': self.valorant.pk,
        })
        self.assertRedirects(response, reverse('tournoi:liste_equipes'))
        self.equipe.refresh_from_db()
        self.assertEqual(self.equipe.capitaine, "Nouveau Capitaine")
        self.assertEqual(self.equipe.email_contact, "nouveau@exemple.com")

    def test_supprimer_get_ne_supprime_pas(self):
        response = self.client.get(reverse('tournoi:equipe_supprimer', args=[self.equipe.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Equipe.objects.filter(pk=self.equipe.pk).exists())

    def test_supprimer_post(self):
        response = self.client.post(reverse('tournoi:equipe_supprimer', args=[self.equipe.pk]))
        self.assertRedirects(response, reverse('tournoi:liste_equipes'))
        self.assertFalse(Equipe.objects.filter(pk=self.equipe.pk).exists())

    def test_modifier_equipe_inexistante_404(self):
        response = self.client.get(reverse('tournoi:equipe_modifier', args=[9999]))
        self.assertEqual(response.status_code, 404)


class CrudJeuTests(TestCase):

    def test_ajouter_jeu(self):
        response = self.client.post(reverse('tournoi:jeu_ajouter'), {
            'nom': "Rocket League", 'plateforme': "PC",
            'nombre_joueurs_equipe': 3, 'actif': True,
        })
        jeu = Jeu.objects.get(nom="Rocket League")
        self.assertRedirects(response, reverse('tournoi:jeu_detail', args=[jeu.pk]))

    def test_ajouter_jeu_zero_joueur_refuse(self):
        response = self.client.post(reverse('tournoi:jeu_ajouter'), {
            'nom': "X", 'plateforme': "PC", 'nombre_joueurs_equipe': 0,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Jeu.objects.filter(nom="X").exists())
