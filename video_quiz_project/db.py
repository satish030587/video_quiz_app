from django.db.backends.postgresql import base
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.backends.postgresql.introspection import DatabaseIntrospection
from django.db.backends.postgresql.operations import DatabaseOperations
from django.apps import apps

class MappedDatabaseIntrospection(DatabaseIntrospection):
    def get_table_list(self, cursor):
        tables = super().get_table_list(cursor)
        return tables
        
    def get_table_description(self, cursor, table_name):
        # Map the model table name to the actual database table name
        from video_quiz_project.routers import DatabaseRouter
        if table_name in DatabaseRouter.TABLE_MAP and DatabaseRouter.TABLE_MAP[table_name]:
            table_name = DatabaseRouter.TABLE_MAP[table_name]
        return super().get_table_description(cursor, table_name)
        
    def get_sequences(self, cursor, table_name, table_fields=()):
        # Map the model table name to the actual database table name
        from video_quiz_project.routers import DatabaseRouter
        if table_name in DatabaseRouter.TABLE_MAP and DatabaseRouter.TABLE_MAP[table_name]:
            table_name = DatabaseRouter.TABLE_MAP[table_name]
        return super().get_sequences(cursor, table_name, table_fields)
        
    def get_key_columns(self, cursor, table_name):
        # Map the model table name to the actual database table name
        from video_quiz_project.routers import DatabaseRouter
        if table_name in DatabaseRouter.TABLE_MAP and DatabaseRouter.TABLE_MAP[table_name]:
            table_name = DatabaseRouter.TABLE_MAP[table_name]
        return super().get_key_columns(cursor, table_name)
        
    def get_constraints(self, cursor, table_name):
        # Map the model table name to the actual database table name
        from video_quiz_project.routers import DatabaseRouter
        if table_name in DatabaseRouter.TABLE_MAP and DatabaseRouter.TABLE_MAP[table_name]:
            table_name = DatabaseRouter.TABLE_MAP[table_name]
        return super().get_constraints(cursor, table_name)

class MappedDatabaseSchemaEditor(DatabaseSchemaEditor):
    def quote_name(self, name):
        # Map the model table name to the actual database table name
        from video_quiz_project.routers import DatabaseRouter
        if name in DatabaseRouter.TABLE_MAP and DatabaseRouter.TABLE_MAP[name]:
            name = DatabaseRouter.TABLE_MAP[name]
        return super().quote_name(name)

class DatabaseOperations(DatabaseOperations):
    def quote_name(self, name):
        # Map the model table name to the actual database table name
        from video_quiz_project.routers import DatabaseRouter
        if name in DatabaseRouter.TABLE_MAP and DatabaseRouter.TABLE_MAP[name]:
            name = DatabaseRouter.TABLE_MAP[name]
        return super().quote_name(name)

class DatabaseWrapper(base.DatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.introspection = MappedDatabaseIntrospection(self)
        self.ops = DatabaseOperations(self)
        
    def schema_editor(self, *args, **kwargs):
        return MappedDatabaseSchemaEditor(self, *args, **kwargs)
