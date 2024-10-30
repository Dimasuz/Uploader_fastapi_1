import datetime
import warnings
from http.client import responses

import pytest
from fastapi.utils import create_response_field

from .api_client import HttpError, FileApiClient
from .constants import DEFAULT_USER_PASSWORD, DEFAULT_USER_EMAIL

warnings.filterwarnings(action="ignore")


class TestUser:
    def test_create_user(self, client: FileApiClient):
        request_time = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        create_response = client.create_user("test_create_user_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        response_time = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        assert create_response.email == "test_create_user_"+DEFAULT_USER_EMAIL
        assert request_time <= datetime.datetime.fromisoformat(create_response.registration_time) <= response_time
        client.delete_user("test_create_user_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)


    def test_create_user_with_existing_email(self, client: FileApiClient):
        client.create_user("test_create_user_with_existing_email_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        with pytest.raises(HttpError) as err:
            client.create_user("test_create_user_with_existing_email_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
            assert err.value.status_code == 400
        client.delete_user("test_create_user_with_existing_email_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)

    def test_confirm_email(self, client: FileApiClient):
        confirm_response = client.confirm_user("test_confirm_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        assert confirm_response.roles == ['user']
        client.delete_user("test_confirm_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)

    def test_login(self, client: FileApiClient):
        client.confirm_user("test_login_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        response = client.login("test_login_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        assert response.token is not None
        client.delete_user("test_login_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)

    def test_login_no_confirm(self, client: FileApiClient):
        client.create_user("test_no_confirm_login_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        with pytest.raises(HttpError) as err:
            client.login("test_no_confirm_login_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
            assert err.value.status_code == 401
            assert err.value.description == '{"detail":"Confirm your email."}'
        client.delete_user("test_no_confirm_login_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)

    def test_get_user(self, client: FileApiClient):
        client.confirm_user("test_get_user_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        client.auth("test_get_user_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        user = client.get_user()
        assert user.email == "test_get_user_"+DEFAULT_USER_EMAIL
        client.delete_user("test_get_user_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)

    def test_update_user_email(self, client: FileApiClient):
        client.confirm_user("test_update_user_email"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        client.auth("test_update_user_email"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        update_response = client.update_user(email="test_update_user_email_new_email"+DEFAULT_USER_EMAIL)
        assert update_response.email == "test_update_user_email_new_email"+DEFAULT_USER_EMAIL
        client.delete_user("test_update_user_email_new_email"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)

    def test_update_user_password(self, client: FileApiClient):
        client.confirm_user("test_update_user_password"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        client.auth("test_update_user_password"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        client.update_user(password="new"+DEFAULT_USER_PASSWORD)
        login_response = client.login("test_update_user_password"+DEFAULT_USER_EMAIL, "new" + DEFAULT_USER_PASSWORD)
        assert login_response.token is not None
        client.delete_user("test_update_user_password"+DEFAULT_USER_EMAIL, "new"+DEFAULT_USER_PASSWORD)

    # def test_update_no_permission(self, client: FileApiClient, admin_client: FileApiClient):
    #     client.confirm_user("test_update_no_permission_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
    #     client.auth("test_update_no_permission_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
    #     response = client.confirm_user("test_update_no_permission2_"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
    #     with pytest.raises(HttpError) as err:
    #         client.update_user(email="test_update_no_permission_new_email"+DEFAULT_USER_EMAIL)
    #     assert err.value.status_code == 403
    #     # admin_client.delete_user(create_response.id)
    #     # admin_client.delete_user(response.id)

    def test_delete_user(self, client: FileApiClient):
        client.confirm_user("test_delete_user"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        client.auth("test_delete_user"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        delete_response = client.delete_user("test_delete_user"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        assert delete_response.status == "deleted"
        with pytest.raises(HttpError) as err:
            client.get_user()
        assert err.value.status_code == 401  # token was deleted with user
        with pytest.raises(HttpError) as err:
            client.login("test_delete_user"+DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
        # assert 0



# # pytest tests/test_user.py
