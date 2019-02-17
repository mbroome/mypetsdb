ALTER TABLE cares_xref CHANGE COLUMN code category VARCHAR(10);
ALTER TABLE iucn_redlist_xref CHANGE COLUMN code category VARCHAR(10);
ALTER TABLE species_data CHANGE COLUMN iucn_id iucn_link VARCHAR(255);


