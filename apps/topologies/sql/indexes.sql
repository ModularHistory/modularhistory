-- Add an index to be used when the path is accessed directly.
CREATE INDEX {app_name}_{model_name}_path ON {app_name}_{model_name} USING btree(path);

-- Add an index to be used for descendants or ancestors.
CREATE INDEX {app_name}_{model_name}_path_gist ON {app_name}_{model_name} USING GIST(path);
