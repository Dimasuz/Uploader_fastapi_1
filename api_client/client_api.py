import os.path
import time
import uuid
from datetime import datetime
from pprint import pprint
from tempfile import NamedTemporaryFile

import requests

TOKEN = ""
# TOKEN = "12674c1a-011f-441f-af7d-3a967aaae73b"

# url_adress = "0:0:0:0"
url_adress = "127.0.0.1"
# url_adress = "89.111.174.234"

url_port = "8000"
api_version = "v1"

url_base = f"http://{url_adress}:{url_port}/{api_version}/"
# url_base = 'http://0.0.0.0:8000/api/v1/auth0/'

# add_url_file_view = ""
# add_url_file_view = "mongo/"

time_now = str(datetime.now()).replace(":", "-").replace(" ", "_")


def base_request(
        url_view="",
        method="get",
        headers=None,
        data=None,
        params=None,
        files=None,
        json=None,
        ):
    url = url_base + url_view
    print()
    print(method, url_view)
    if method == "get":
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=60,
            verify=False
        )
    if method == "post":
        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files,
            json=json
        )
    if method == "put":
        response = requests.put(
            url,
            headers=headers,
            json=data,
        )
    if method == "delete":
        response = requests.delete(
            url,
            json=json,
        )
    print(response.url)
    # print(response.headers)
    print(response.status_code)
    if response.status_code != 204:
        try:
            response.json()
            print("JSON:")
            pprint(response.json())
        except BaseException as e:
            print("ERROR.")
            pprint(e)
            print("RESPONSE TEXT:")
            pprint(response.text)
            return response, False

    return response, True


def get_headers(token=None, content_type=None):
    authorization = f"Token {token}"
    if content_type:
        headers = {
            "Content-Type": content_type,
            "Authorization": authorization,
        }
    else:
        headers = {
            # "Authorization": authorization,
            "x-token": token,
        }
    return headers

# hello
def home_get():
    url_view = "home/"
    response, json_status = base_request(
        url_view=url_view,
        method="get",
    )
    return response


# users get
def users_get():
    url_view = "users/"
    response, json_status = base_request(
        url_view=url_view,
        method="get",
    )
    return response


# registration-----------
def user_register(email=None, password=None, **kwargs):
    # url_view = "user/register/"
    url_view = "user/"
    if kwargs:
        data = kwargs
    else:
        data = {}
    if not email:
        email = input("Введите email: ")
    if not password:
        password = input("Введите пароль или Enter: ")
        if not password:
            password = f"Password_{email}"
    data["email"] = email
    data["password"] = password
    # print(data)
    response, json_status = base_request(url_view=url_view, method="post", json=data,)
    if json_status:
        # print(response.json())
        id = response.json()["id"]
        token = response.json()["token"]
    else:
        id = None
        token = None
    # if response.status_code == 201 and json_status:
    #     if response.json()["Status"] == False:
    #         # task_id = None
    #         # token_confirm = None
    #         id = None
    #     else:
    #         # task_id = response.json()["Task_id"]
    #         # token_confirm = response.json()["token"]
    #         id = response.json()["id"]
    # else:
    #     # task_id = None
    #     # token_confirm = None
    #     id = None
    # return task_id, token_confirm
    return id, token

# confirm email----------------------
def confirm(email=None, token=None):
    url_view = "user/register/confirm/"
    if not email:
        email = input("Введите email пользователя: ")
    if not token:
        token = input("Введите token: ")
    data = {
        "email": email,
        "token": token,
    }
    response, json_status = base_request(url_view=url_view, method="post", data=data)
    return response


# login user -----------------------
def login(email=None, password=None):
    # url_view = "user/login/"
    url_view = "login/"
    if not email:
        email = input("Введите email пользователя = ")
    if not password:
        password = f"Password_{email}"
    data = {
        "email": email,
        "password": password,
    }
    response, json_status = base_request(url_view=url_view, method="post", json=data)
    if json_status:
        token_login = response.json()["token"]
    else:
        token_login = None
    # if response.status_code == 202 and json_status:
    #     if response.json()["Status"] == False:
    #         token_login = None
    #     else:
    #         token_login = response.json()["Token"]
    # else:
    #     token_login = None
    return token_login


# user/details/ -----------------------------
def details_get(token=None,):
    # url_view = "user/details/"
    url_view = "user/"
    if not token:
        token = input("Введите token пользователя = ")
    headers = get_headers(token=token)
    response, json_status = base_request(
        url_view=url_view,
        method="get",
        headers=headers,
    )
    return response


def details_put(token=None, **kwargs):
    # url_view = "user/details/"
    url_view = "user/"
    if not token:
        token = input("Введите token пользователя = ")
    headers = get_headers(token=token)
    response, json_status = base_request(
        url_view=url_view, method="put", data=kwargs, headers=headers
    )
    return response


# logout user-----------------------
def logout(token=None):
    url_view = "user/logout/"
    if not token:
        token = input("Введите token пользователя = ")
    headers = get_headers(token=token)
    response, json_status = base_request(
        url_view=url_view,
        method="post",
        headers=headers,
    )
    return response


# delete user-----------------------
def delete(email=None, password=None):
    url_view = "user/"
    if not email:
        email = input("Введите email пользователя = ")
    if not password:
        password = input("Введите password пользователя = ")
    data = {
        "email": email,
        "password": password,
    }
    response, json_status = base_request(
        url_view=url_view,
        method="delete",
        json=data,
    )
    return response


# /user/password_reset/ ----------------------------
def password_reset(email=None):
    url_view = "user/password_reset/"
    if not email:
        email = input("Введите email пользователя = ")
    data = {
        "email": email,
    }
    response, json_status = base_request(url_view=url_view, method="post", data=data)


# /user/password_reset/confirm/ ----------------------------
def password_reset_confirm(token=None, password=None):
    url_view = "user/password_reset/confirm/"
    if not token:
        token = input("Введите token = ")
    if not password:
        password = input("Введите password = ")
    data = {
        "token": token,
        "password": password,
    }
    response, json_status = base_request(url_view=url_view, method="post", data=data)


# ------------------------------------
# FILE

# file/upload/
def upload(token=None, data=None):
    url_view = f"file/{add_url_file_view}"
    if not token:
        token = input("Введите token пользователя = ")
    headers = get_headers(token=token)
    uploaded_file_time = time_now
    uploaded_file_name = f"test_{uploaded_file_time[:19]}_uploaded_file.txt"
    with NamedTemporaryFile(
        "w+b", prefix="uploaded_file_name", suffix="uploaded_file_ext"
    ) as f:
        f.write(f"<begin - client_api_test - {uploaded_file_time} - end>".encode())
        f.seek(0)
        files = {"file": (uploaded_file_name, f, "text/x-spam")}
        try:
            response, json_status = base_request(
                url_view=url_view,
                method="post",
                headers=headers,
                files=files,
                data=data,
            )
            return response
        except Exception as e:
            return e


# file/download/
def download(
    token=None,
    file_id=None,
):
    url_view = f"file/{add_url_file_view}"
    if not token:
        token = input("Введите token пользователя = ")
    if not file_id:
        file_id = input("Введите file_id = ")
    headers = get_headers(token=token)
    params = {
        "file_id": file_id,
    }
    response, json_status = base_request(
        url_view=url_view,
        method="get",
        headers=headers,
        params=params,
    )
    if response.status_code == 200:

        filename = response.headers.get("Content-Disposition")
        start_index = filename.find("filename=") + 10
        filename = filename[start_index:-1]

        # downloaded_file_name = f"test_{response.text[9:28]}_download_file.txt"
        downloaded_file_time = time_now
        downloaded_file_name = (
            f"test_{filename}_download_time_{downloaded_file_time[:19]}.txt"
        )
        CURR_DIR = os.path.dirname(os.path.realpath(__file__))
        downloaded_file = os.path.join(CURR_DIR, downloaded_file_name)

        with open(downloaded_file, "wb+") as f:
            f.write(response.content)
            # f.write(filename.encode('utf-8'))
        print("File downloaded:")
        with open(downloaded_file, "rb") as f:
            print(f.read())
        # time.sleep(5)
        if os.path.isfile(downloaded_file):
            os.remove(downloaded_file)
            if not os.path.isfile(downloaded_file):
                print("Downloaded file deleted.")
    else:
        return response


# file/processing/
def processing(token=None, file_id=None):
    url_view = f"file/{add_url_file_view}"
    if not token:
        token = input("Введите token пользователя = ")
    if not file_id:
        file_id = input("Введите file_id = ")
    headers = get_headers(token=token)
    data = {
        "file_id": file_id,
    }
    response, json_status = base_request(
        url_view=url_view,
        method="put",
        headers=headers,
        data=data,
    )

    return response


# file/delete/
def file_delete(token=None, file_id=None):
    url_view = f"file/{add_url_file_view}"
    if not token:
        token = input("Введите token пользователя = ")
    if not file_id:
        file_id = input("Введите file_id = ")
    headers = get_headers(token=token)
    data = {
        "file_id": file_id,
    }
    response, json_status = base_request(
        url_view=url_view,
        method="delete",
        headers=headers,
        data=data,
    )

    return response


# celery tesk status-----------------------
def celery_status(task_id=None):
    url_view = "celery_status/"
    if not task_id:
        task_id = input("Введите task_id = ")
    if task_id:
        celery_status = "-"
        while celery_status != "SUCCESS":
            #  or celery_status != 'FAILURE'
            response, json_status = base_request(
                url_view=url_view, method="get", params={"task_id": task_id}
            )
            celery_status = response.json()["Status"]
            # file = response.json()["Result"]
            time.sleep(1)
            # if not celery_status == "SUCCESS":
            #     if input("Stop? y/n") == "y":
            #         return celery_status
        return celery_status


def api_test(token=None, url_store="disk"):
    a = input("1 - users, \n2 - files\n3 - home\n: ")
    if a == "1":
        a = input(
            "1 - user registration,\n2 - email confirm,\n3 - login,\n4 - logout,\n"
            "5 - delete user,\n6 - user deteils get,\n7 - user deteils change,\n"
            "8 - task get,\n11 - reset password,\n0 - all user operations\n: "
        )
        # регистраиця нового пользователя
        if a == "0":
            print("\nUSER REGISTRATION:")
            # email = str(uuid.uuid4())[:5]
            email = '6021185'
            email = email + "@mail.ru"
            password = f"Password_{email}"
            task, token = user_register(email=email, password=password)
            print("\nCONFIRM USER EMAIL:")
            confirm(email=email, token=token)
            print("\nLOGIN USER:")
            token = login(email=email, password=password)
            print("\nGET USER DETAILS:")
            data_old = details_get(token).json()
            print(f'\nCHANGE USER DETAILS:')
            password_new = f"new_Password_{email}"
            data = {
                "first_name": f"new_{time_now}_{data_old['first_name']}",
                "last_name": f"new_{time_now}_{data_old['last_name']}",
                "password": password_new,
            }
            # details_post(token=token, **data)
            print("\nGET NEW DETAILS:")
            details_get(token=token)
            print("\nLOGOUT USER:")
            logout(token)
            print("\nLOGIN USER WITH NEW PASSWORD:")
            token = login(email=email, password=password_new)
            details_get(token)
            print("\nUSER DELETE:")
            response = delete(token)
            if response.status_code == 204:
                print("\nGREATE!")
            else:
                print("\nSomething was going wrong...")
        elif a == "10":
            print("\nUSER REGISTRATION:")
            email = str(uuid.uuid4())[:5]
            # email = '6021185'
            email = email + "@mail.ru"
            password = f"Password_{email}"
            data = {
                "first_name": f"First_name_{email}",
            }
            # task, token = user_register(email=email, password=password)
            user_id, token = user_register(email=email, password=password, **data)
            print("\nCONFIRM USER EMAIL:")
            details_put(token=token,)
            print("\nLOGIN USER:")
            token = login(email=email, password=password)
            print("\nGET USER DETAILS:")
            data_old = details_get(token=token).json()
            print(f'\nCHANGE USER DETAILS:')
            new_email = f"new_{data_old['email']}"
            new_password = f"new_Password_{email}"
            data = {
                "first_name": f"new_first_name_{email}",
                "last_name": f"new_last_name_{email}",
                "email": new_email,
                "password": new_password,
            }
            details_put(token=token, **data)
            # print("\nGET NEW DETAILS:")
            # details_get(token=token)
            # print("\nLOGOUT USER:")
            # logout(token)
            # print("\nLOGIN USER WITH NEW PASSWORD:")
            # token = login(email=email, password=password_new)
            print("\nGET USER NEW DETAILS:")
            data_new = details_get(token=token).json()
            print("\nUSER DELETE:")
            response = delete(email=new_email, password=new_password)
            # if response.status_code == 204:
            if response.json()["status"] == "deleted":
                print("\nGREATE!")
            else:
                print("\nSomething was going wrong...")

        elif a == "11":
            email = "5845889@mail.ru"
            password = f"Password_{email}"
            delete(email=email, password=password)
            user_register(email=email, password=password)

        elif a == "1":
            email = input("Введите {адрес} @mail.ru: ")
            email = email + "@mail.ru"
            if not input("Стандартный пароль? Y(enter)/N"):
                password = f"Password_{email}"
            else:
                password = input("Введите пароль: ")
            user_register(email=email, password=password)
            # celery = input("Запросить очередь celery? ")
            # if celery:
            #     celery_status(response.json()["Task_id"])
            # else:
            #     return
        # подтверждение почты нового пользователя
        elif a == "2":
            email = input("Введите {адрес} @mail.ru: ")
            email = email + "@mail.ru"
            confirm(email=email)
        # вход в систему
        elif a == "3":
            email = input("Введите {адрес} @mail.ru: ")
            email = email + "@mail.ru"
            if not input("Стандартный пароль? Y(enter)/N"):
                login(email=email)
            else:
                password = input("Введите пароль: ")
                login(email=email, password=password)
        # выход из системы
        elif a == "4":
            logout(token=token)
        # удаление пользователя
        elif a == "5":
            email = input("Введите {адрес} @mail.ru: ")
            email = email + "@mail.ru"
            if not input("Стандартный пароль? Y(enter)/N"):
                password = f"Password_{email}"
            else:
                password = input("Введите пароль: ")
            delete(email=email, password=password)

        # запрос данных пользователя
        elif a == "6":
            # email = input("Введите {адрес} @mail.ru: ")
            # email = email + "@mail.ru"
            # token = login(email=email)
            details_get(token)
        # изменение данных пользователя
        elif a == "7":
            email = input("Введите {адрес} @mail.ru: ")
            email = email + "@mail.ru"
            # print("Входим в систему.")
            # token = login(email=email)
            # получаем текущие данные пользователя
            data_old = details_get(token).json()
            print(data_old)
            print(f'Меняем данные пользователя добавив "new_{time_now}_".')
            password_new = f"new_Password_{email}"
            data = {
                "first_name": f"new_{time_now}_{data_old['first_name']}",
                "last_name": f"new_{time_now}_{data_old['last_name']}",
                # "password": password_new,
            }
            # details_post(token=token, **data)
            details_get(token=token)
            print("Выходим из системы")
            logout()
            if input("Меняем данные пользователя обратно? Y "):
                print("Входим в систему.")
                token = login(email=email, password=password_new)
                data = data_old + {"password": f"Password_{email}"}
                # details_post(token, **data)
                details_get(token)
                print("Выходим из системы")
                logout(token)
        # запрос таски
        elif a == "8":
            celery_status()
        elif a == "11":
            password_reset()
            password_reset_confirm()
    elif a == "2":
        b = input("postgres/sqlite3 - 1\nmongo - 2\nВыберете базу данных: ")
        global add_url_file_view
        if b == "1":
            add_url_file_view = ""
        elif b == "2":
            add_url_file_view = "mongo/"
        a = input(
            "0 - file upload, processing, get task, download and all delete,\n"
            "1 - file upload,\n2 - file processing,\n3 - file download,\n4 - file delete,\n: "
        )

        if a == "0":
            print("\nPREPARE USER:")
            email = str(uuid.uuid4())[:5]
            email = email + "@mail.ru"
            password = f"Password_{email}"
            task, token = user_register(email=email, password=password)
            confirm(email=email, token=token)
            token = login(email=email, password=password)
            print("\nUPLOAD FILE BY ASYNC:")
            data = {"sync_mode": False}
            file_id_1 = upload(token=token, data=data).json()["File_id"]
            print(f"Uploaded file with {file_id_1=}")
            print("\nUPLOAD FILE BY SYNC:")
            data = {"sync_mode": True}
            file_id_2 = upload(token=token, data=data).json()["File_id"]
            print(f"Uploaded file with {file_id_2=}")
            print()
            print(f"PROCESSING OF FILE WITH ID - {file_id_1}.")
            task_id = processing(token=token, file_id=file_id_1)
            # task_id = task_id.json()["Task_id"]
            # print(f"Запрос таски - {task_id}.")
            # print(celery_status(task_id=task_id))
            # print()
            # time.sleep(11)
            # print(f"Запрос таски - {task_id}.")
            # print(celery_status(task_id=task_id))
            print(f"\nDOWNLOAD FILE WITH ID - {file_id_1}:")
            download(token=token, file_id=file_id_1,)
            print("\nDELETE FILES AND USER:")
            print(f"\nDelete file with id - {file_id_1}.")
            file_delete(token=token, file_id=file_id_1)
            print(f"\nDelete file with - {file_id_2}.")
            file_delete(token=token, file_id=file_id_2)
            print(f"\nDelete user.")
            response = delete(token)
            if response.status_code == 204:
                print("\nGREATE!")
            else:
                print("\nSomething was going wrong...")

        elif a == "1":
            print(f"Загрузка файла.")
            data = {"sync_mode": False}
            upload(token=token, data=data)
            # upload(token=token)
        elif a == "2":
            print(f"Обработка файла.")
            file_id = input("file_id = ")
            responce = processing(token=token, file_id=file_id)
            if input("Get celery task result? y"):
                celery_status(responce.json()["Task_id"])
        elif a == "3":
            print(f"Скачивание файла.")
            download(
                token=token,
            )
        elif a == "4":
            print(f"Удаление файла.")
            file_id = input("file_id = ")
            file_delete(token=token, file_id=file_id)
    elif a == '3':
        home_get()
        users_get()
    else:
        pass
    return None


if __name__ == "__main__":
    token = TOKEN

    # url_list = ['disk', 'db']
    # url_store = url_list[1]
    api_test(token=token)

    # curl --location --request POST 'http://localhost:8000/api/upload-file/' \
    # --form 'file=@"/path/to/yourfile.pdf"'

# from django.conf import settings
# from django.core.cache import cache
# cache_keys = cache._cache.get_cient().keys(f"*{settings.CACHES['default']['KEY_PREFIX']}*")
