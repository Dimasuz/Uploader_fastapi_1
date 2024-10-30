import pytest

from .api_client import HttpError
from .conftest import NewUser, FileApiClient
from .constants import NEW_FILE_ITEM_IMPORTANT, NEW_FILE_ITEM_NOT_IMPORTANT


class TestFile:
    @pytest.mark.parametrize(
        "important",
        [
            True,
            False,
        ],
    )
    def test_create_file(self, new_user: NewUser, important: bool):
        response = new_user.client.create_file(name="test_create_file", important=important)
        assert response.id is not None
        assert new_user.client.get_user(new_user.id).files == [response.id]

    def test_create_file_with_empty_name(self, new_user: NewUser):
        with pytest.raises(HttpError) as excinfo:
            new_user.client._call("POST", "/v1/file", json={"important": False})
        assert excinfo.value.status_code == 422

    def test_create_file_without_auth(self, client: FileApiClient, client_without_auth: FileApiClient):
        with pytest.raises(HttpError) as excinfo:
            client.create_file("test_create_file_without_auth")
        assert excinfo.value.status_code == 422

        with pytest.raises(HttpError) as excinfo:
            client_without_auth.create_file("test_create_file_without_auth")
        assert excinfo.value.status_code == 401

    def test_get_files(self, new_user_with_files: NewUser):
        files = new_user_with_files.client.get_files().files
        assert len(files) == 2
        assert files[0].name == NEW_FILE_ITEM_IMPORTANT
        assert files[0].important is True
        assert files[1].name == NEW_FILE_ITEM_NOT_IMPORTANT
        assert files[1].important is False

    def test_get_files_without_auth(self, client: FileApiClient, client_without_auth: FileApiClient):
        with pytest.raises(HttpError) as excinfo:
            client.get_files()
        assert excinfo.value.status_code == 422

        with pytest.raises(HttpError) as excinfo:
            client_without_auth.get_files()
        assert excinfo.value.status_code == 401

    def test_get_file_id(self, new_user_with_files: NewUser):
        files = new_user_with_files.client.get_files().files
        for file in files:
            file_by_id = new_user_with_files.client.get_file(file.id)
            assert file_by_id.id == file.id
            assert file_by_id.name == file.name
            assert file_by_id.important == file.important
            assert file_by_id.done == file.done
            assert file_by_id.start_time == file.start_time
            assert file_by_id.finish_time == file.finish_time

    #
    def test_get_file_id_without_auth(self, client: FileApiClient, client_without_auth: FileApiClient):
        with pytest.raises(HttpError) as excinfo:
            client.get_file(1)
        assert excinfo.value.status_code == 422

        with pytest.raises(HttpError) as excinfo:
            client_without_auth.get_file(1)
        assert excinfo.value.status_code == 401

    def test_get_file_id_with_wrong_id(self, new_user_with_files: NewUser):
        with pytest.raises(HttpError) as excinfo:
            new_user_with_files.client.get_file(9999999)
        assert excinfo.value.status_code == 404

    def test_get_file_id_not_owner(self, user_client: FileApiClient, new_user_with_files: NewUser):
        files = new_user_with_files.client.get_files().files
        for file in files:
            with pytest.raises(HttpError) as excinfo:
                user_client.get_file(file.id)
            assert excinfo.value.status_code == 403

    def test_update_file_name(self, new_user_with_files: NewUser):
        file = new_user_with_files.client.get_files().files[0]
        new_user_with_files.client.update_file(file.id, name="new_name")
        file = new_user_with_files.client.get_file(file.id)
        assert file.name == "new_name"

    def test_update_file_important(self, new_user_with_files: NewUser):
        file = new_user_with_files.client.get_files().files[0]
        new_user_with_files.client.update_file(file.id, important=True)
        file = new_user_with_files.client.get_file(file.id)
        assert file.important is True

    def test_update_file_done(self, new_user_with_files: NewUser):
        file = new_user_with_files.client.get_files().files[0]
        new_user_with_files.client.update_file(file.id, done=True)
        file = new_user_with_files.client.get_file(file.id)
        assert file.done is True
        assert file.finish_time is not None

    def test_delete_file(self, new_user_with_files: NewUser):
        file = new_user_with_files.client.get_files().files[0]
        new_user_with_files.client.delete_file(file.id)
        with pytest.raises(HttpError) as excinfo:
            new_user_with_files.client.get_file(file.id)
        assert excinfo.value.status_code == 404

    def test_update_alien_file(self, new_user_with_files: NewUser, user_client: FileApiClient):
        file = new_user_with_files.client.get_files().files[0]
        with pytest.raises(HttpError) as excinfo:
            user_client.update_file(file.id, name="new_name")
        assert excinfo.value.status_code == 403

    def test_admin_update_alien_file(self, new_user_with_files: NewUser, admin_client: FileApiClient):
        file = new_user_with_files.client.get_files().files[0]
        admin_client.update_file(file.id, name="new_name")
        file = new_user_with_files.client.get_file(file.id)
        assert file.name == "new_name"
