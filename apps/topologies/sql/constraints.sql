-- Prevent a model instance from having itself as an ancestor (which would result in an infinite recursion).
ALTER TABLE {app_name}_{model_name} ADD CONSTRAINT check_no_recursion
    CHECK(index(path, key::text::ltree) = (nlevel(path) - 1));
