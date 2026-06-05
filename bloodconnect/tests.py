from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from bloodconnect.i18n import LANGUAGE_SESSION_KEY, translate_text


class LocalizationTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def test_translate_text_falls_back_to_original_when_key_missing(self):
        self.assertEqual(translate_text("Missing translation key", "hi"), "Missing translation key")

    def test_set_language_persists_language_in_session(self):
        response = self.client.get(reverse("set_language", args=["hi"]), {"next": reverse("home")})

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(self.client.session[LANGUAGE_SESSION_KEY], "hi")

    def test_authenticated_homepage_exposes_language_switch(self):
        user = self.user_model.objects.create_user(
            username="language-test-user",
            password="password123",
            role="donor",
        )
        self.client.force_login(user)

        session = self.client.session
        session[LANGUAGE_SESSION_KEY] = "hi"
        session.save()

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_language"], "hi")
        self.assertEqual(response.context["current_language_label"], "हिन्दी")
        self.assertContains(response, "हिन्दी")
