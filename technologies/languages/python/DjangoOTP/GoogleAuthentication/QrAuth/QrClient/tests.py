import base64
from binascii import unhexlify

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
from QrClient.views import (
    PENDING_TOTP_SESSION_KEY,
    PENDING_TOTP_USER_SESSION_KEY,
)
from two_factor.utils import totp_digits


class QrClientSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="owner-pass-123"
        )
        self.other = User.objects.create_user(
            username="other", password="other-pass-123"
        )
        self.client = Client()

    def _store_pending(self, user, key=None):
        key = key or random_hex(20)
        session = self.client.session
        session[PENDING_TOTP_SESSION_KEY] = key
        session[PENDING_TOTP_USER_SESSION_KEY] = user.pk
        session.save()
        return key

    def _token_for_key(self, key):
        return str(
            totp(unhexlify(key.encode("ascii")), step=30, digits=totp_digits())
        ).zfill(totp_digits())

    def test_unauthenticated_list_get_is_rejected(self):
        response = self.client.get("/qrClient/api/v1/qrcode/list/")
        self.assertIn(response.status_code, (401, 403))

    def test_unauthenticated_list_post_is_rejected(self):
        response = self.client.post(
            "/qrClient/api/v1/qrcode/list/",
            data={"token": "123456"},
            content_type="application/json",
        )
        self.assertIn(response.status_code, (401, 403))

    def test_unauthenticated_save_get_is_rejected(self):
        response = self.client.get("/qrClient/api/v1/qrcode/save")
        self.assertIn(response.status_code, (401, 403))

    def test_unauthenticated_save_post_is_rejected(self):
        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={"user": "owner", "key": "abc", "token": "123456"},
            content_type="application/json",
        )
        self.assertIn(response.status_code, (401, 403))

    def test_authenticated_user_cannot_create_device_for_another_username(self):
        self.client.force_login(self.owner)
        key = self._store_pending(self.owner)
        token = self._token_for_key(key)
        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={"user": "other", "token": token},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(TOTPDevice.objects.filter(user=self.other).exists())
        self.assertFalse(TOTPDevice.objects.filter(user=self.owner).exists())

    def test_enroll_post_does_not_return_jwt_without_verified_totp(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={"user": "owner", "key": random_hex(20)},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertNotIn("api_token", payload)
        self.assertNotIn("refreshToken", payload)
        self.assertFalse(TOTPDevice.objects.filter(user=self.owner).exists())

    def test_list_is_scoped_to_request_user_and_omits_key(self):
        TOTPDevice.objects.create(
            user=self.owner,
            key=random_hex(20),
            name="owner-device",
            confirmed=True,
        )
        TOTPDevice.objects.create(
            user=self.other,
            key=random_hex(20),
            name="other-device",
            confirmed=True,
        )

        self.client.force_login(self.owner)
        response = self.client.get("/qrClient/api/v1/qrcode/save")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["name"], "owner-device")
        self.assertNotIn("key", payload[0])

    def test_qrsetup_post_verifies_totp_without_nameerror(self):
        self.client.force_login(self.owner)
        key = self._store_pending(self.owner)
        token = self._token_for_key(key)
        response = self.client.post(
            "/qrClient/api/v1/qrcode/list/",
            data={"token": token},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertNotIn("key", payload)
        self.assertNotIn("api_token", payload)
        self.assertNotIn("refreshToken", payload)
        device = TOTPDevice.objects.get(user=self.owner, confirmed=True)
        self.assertGreaterEqual(device.last_t, 0)

    def test_basic_auth_allows_ordinary_user_to_request_qr(self):
        credentials = base64.b64encode(b"owner:owner-pass-123").decode("ascii")
        response = self.client.get(
            "/qrClient/api/v1/qrcode/list/",
            HTTP_AUTHORIZATION=f"Basic {credentials}",
            HTTP_ACCEPT="image/svg+xml",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("image/svg+xml", response["Content-Type"])
        self.assertTrue(response.content)

    def test_null_device_name_is_rejected_without_integrity_error(self):
        self.client.force_login(self.owner)
        key = self._store_pending(self.owner)
        token = self._token_for_key(key)
        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={"token": token, "name": None},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(TOTPDevice.objects.filter(user=self.owner).exists())

    def test_overlong_device_name_is_rejected(self):
        self.client.force_login(self.owner)
        key = self._store_pending(self.owner)
        token = self._token_for_key(key)
        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={"token": token, "name": "x" * 65},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(TOTPDevice.objects.filter(user=self.owner).exists())

    def test_password_only_cannot_enroll_additional_device(self):
        existing_key = random_hex(20)
        TOTPDevice.objects.create(
            user=self.owner,
            key=existing_key,
            name="primary",
            confirmed=True,
        )
        credentials = base64.b64encode(b"owner:owner-pass-123").decode("ascii")
        new_key = random_hex(20)
        token = self._token_for_key(new_key)
        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={"key": new_key, "token": token},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Basic {credentials}",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(TOTPDevice.objects.filter(user=self.owner).count(), 1)

    def test_existing_otp_allows_additional_enrollment(self):
        existing_key = random_hex(20)
        TOTPDevice.objects.create(
            user=self.owner,
            key=existing_key,
            name="primary",
            confirmed=True,
        )
        self.client.force_login(self.owner)
        new_key = self._store_pending(self.owner)
        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={
                "token": self._token_for_key(new_key),
                "existing_otp": self._token_for_key(existing_key),
                "name": "backup",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            TOTPDevice.objects.filter(user=self.owner, confirmed=True).count(), 2
        )

    def test_pending_secret_bound_to_requesting_user(self):
        self.client.force_login(self.owner)
        key = self._store_pending(self.owner)
        self.client.logout()
        self.client.force_login(self.other)
        # Re-attach the same session pending values after login swap.
        session = self.client.session
        session[PENDING_TOTP_SESSION_KEY] = key
        session[PENDING_TOTP_USER_SESSION_KEY] = self.owner.pk
        session.save()

        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={"token": self._token_for_key(key)},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(TOTPDevice.objects.filter(user=self.other).exists())
        self.assertFalse(TOTPDevice.objects.filter(user=self.owner).exists())

    def test_client_supplied_key_fallback_is_rejected(self):
        """Even a well-formed 40-char hex key is rejected without a pending session."""
        self.client.force_login(self.owner)
        client_key = "0" * 40
        token = self._token_for_key(client_key)
        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={"key": client_key, "token": token},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        detail = response.json()["detail"]
        self.assertIn("pending", detail.lower())
        self.assertIn("client-supplied", detail.lower())
        self.assertFalse(TOTPDevice.objects.filter(user=self.owner).exists())

    def test_random_looking_client_key_without_pending_is_rejected(self):
        self.client.force_login(self.owner)
        client_key = random_hex(20)
        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={"key": client_key, "token": self._token_for_key(client_key)},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(TOTPDevice.objects.filter(user=self.owner).exists())

    def test_enrollment_token_updates_last_t(self):
        self.client.force_login(self.owner)
        key = self._store_pending(self.owner)
        token = self._token_for_key(key)
        response = self.client.post(
            "/qrClient/api/v1/qrcode/save",
            data={"token": token},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        device = TOTPDevice.objects.get(user=self.owner)
        self.assertGreaterEqual(device.last_t, 0)
        # Same token must not verify again (replay consumed via last_t).
        self.assertFalse(device.verify_token(token))

    def test_qr_get_rejects_json_accept(self):
        self.client.force_login(self.owner)
        response = self.client.get(
            "/qrClient/api/v1/qrcode/list/",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 406)
