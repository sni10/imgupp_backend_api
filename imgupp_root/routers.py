
class AppRouter:
    def db_for_read(self, model, **hints):
        """Определяет, из какой базы данных читать для модели."""
        if model._meta.app_label == 'photomanager':
            return 'photomanager_db'
        elif model._meta.app_label == 'users':
            return 'users_db'
        return None

    def db_for_write(self, model, **hints):
        """Определяет, в какую базу данных писать для модели."""
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        """Разрешает ли создавать отношения между объектами из разных баз данных."""
        db1 = self.db_for_read(obj1.__class__)
        db2 = self.db_for_read(obj2.__class__)
        if db1 == db2:
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Определяет, должна ли миграция применяться на данную базу данных."""
        if app_label == 'photomanager':
            return db == 'photomanager_db'
        elif app_label == 'users':
            return db == 'users_db'
        return db == 'default'
