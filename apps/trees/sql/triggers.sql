-- Add a function to calculate the path of a model instance.
CREATE OR REPLACE FUNCTION _update_{app_name}_{model_name}_path() RETURNS TRIGGER AS
$$
BEGIN
    IF NEW.parent_id IS NULL THEN
        NEW.path = NEW.key::ltree;
    ELSE
        SELECT path || NEW.key
          FROM {app_name}_{model_name}
         WHERE NEW.parent_id IS NULL or id = NEW.parent_id
          INTO NEW.path;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add a function to update the path of the descendants of a model instance.
CREATE OR REPLACE FUNCTION _update_descendants_{app_name}_{model_name}_path() RETURNS TRIGGER AS
$$
BEGIN
    UPDATE {app_name}_{model_name}
       SET path = NEW.path || subpath({app_name}_{model_name}.path, nlevel(OLD.path))
     WHERE {app_name}_{model_name}.path <@ OLD.path AND id != NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Recalculate a model instance's path whenever a new model instance is inserted.
DROP TRIGGER IF EXISTS {app_name}_{model_name}_path_insert_trg ON {app_name}_{model_name};
CREATE TRIGGER {app_name}_{model_name}_path_insert_trg
               BEFORE INSERT ON {app_name}_{model_name}
               FOR EACH ROW
               EXECUTE PROCEDURE _update_{app_name}_{model_name}_path();

-- Recalculate a model instance's path when its parent or key are updated.
DROP TRIGGER IF EXISTS {app_name}_{model_name}_path_update_trg ON {app_name}_{model_name};
CREATE TRIGGER {app_name}_{model_name}_path_update_trg
               BEFORE UPDATE ON {app_name}_{model_name}
               FOR EACH ROW
               WHEN (OLD.parent_id IS DISTINCT FROM NEW.parent_id
                     OR OLD.key IS DISTINCT FROM NEW.key)
               EXECUTE PROCEDURE _update_{app_name}_{model_name}_path();

-- When a path is updated, update the path of the model instance's descendants as well.
DROP TRIGGER IF EXISTS {app_name}_{model_name}_path_after_trg ON {app_name}_{model_name};
CREATE TRIGGER {app_name}_{model_name}_path_after_trg
               AFTER UPDATE ON {app_name}_{model_name}
               FOR EACH ROW
               WHEN (NEW.path IS DISTINCT FROM OLD.path)
               EXECUTE PROCEDURE _update_descendants_{app_name}_{model_name}_path();
