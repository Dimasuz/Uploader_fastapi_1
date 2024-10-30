import os
import uuid

DEFAULT_USER_EMAIL = str(uuid.uuid4())[:5] + "test_user_1@mail.ma"
DEFAULT_USER_PASSWORD = "TestPassword41"
NEW_USER_NAME = "test_user_new_user_name"
NEW_USER_NAME_WITH_FILES = "test_user_new_user_name_with_files"
NEW_FILE_ITEM_IMPORTANT = "new_file_item_important"
NEW_FILE_ITEM_NOT_IMPORTANT = "new_file_item_not_important"
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@adm.in")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Password_admin")
