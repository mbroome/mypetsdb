ALTER TABLE cares_xref CHANGE COLUMN scientific_name scientific_name VARCHAR(100);
ALTER TABLE common_names_xref CHANGE COLUMN scientific_name scientific_name VARCHAR(100);
ALTER TABLE pet_data CHANGE COLUMN scientific_name scientific_name VARCHAR(100);
ALTER TABLE planetcatfish_xref CHANGE COLUMN scientific_name scientific_name VARCHAR(100);
ALTER TABLE seriouslyfish_xref CHANGE COLUMN scientific_name scientific_name VARCHAR(100);
ALTER TABLE species_data CHANGE COLUMN scientific_name scientific_name VARCHAR(100);
ALTER TABLE species_names_xref CHANGE COLUMN scientific_name scientific_name VARCHAR(100);
ALTER TABLE species_variety_data CHANGE COLUMN scientific_name scientific_name VARCHAR(100);

ALTER TABLE pet_data CHANGE COLUMN variety variety VARCHAR(50);
ALTER TABLE species_variety_data CHANGE COLUMN variety variety VARCHAR(50);

