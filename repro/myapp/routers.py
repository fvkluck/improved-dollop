class Router:
    def db_for_read(self, model, **hints):
        if model._meta.model_name == "somesecondarymodel":
            return "secondary"

    def db_for_write(self, model, **hints):
        if model._meta.model_name == "somesecondarymodel":
            return "secondary"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if "target_db" in hints:
            return hints["target_db"] == db

        if db == "secondary":
            return model_name == "somesecondarymodel"
        elif model_name == "somesecondarymodel":
            return False
