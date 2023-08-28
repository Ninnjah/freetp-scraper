from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy import create_engine

from models.file import File


class UserAdmin(ModelView, model=File):
    column_list = [File.id, File.name, File.ext, File.url, File.size, File.created_at]
    column_sortable_list = [File.id, File.name, File.ext, File.size, File.created_at]


def app_init(app: FastAPI, db_url: str) -> None:
    engine = create_engine(db_url)
    admin = Admin(app, engine)

    admin.add_view(UserAdmin)
