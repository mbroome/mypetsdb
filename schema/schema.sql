create table species_data (
   scientific_name     VARCHAR(100) NOT NULL,
   common_name         VARCHAR(100) NOT NULL,
   endangered_status   BOOLEAN NOT NULL DEFAULT 0,
   iucn_category       ENUM('DD', 'LC', 'NT', 'VU', 'EN', 'CR', 'EW', 'EX', 'LR/lc', 'LR/nt', 'LR/cd'),
   iucn_id             VARCHAR(20),
   cares               BOOLEAN NOT NULL DEFAULT 0,
   family              VARCHAR(40) NOT NULL,
   genus               VARCHAR(40) NOT NULL,
   species             VARCHAR(40) NOT NULL,
   primary key         (scientific_name)
);

create table pet_data (
   pet_id              VARCHAR(100) NOT NULL,
   scientific_name     VARCHAR(100) NOT NULL,
   variant             VARCHAR(100),
   collection_point    VARCHAR(100),
   userid              VARCHAR(100) NOT NULL,
   start               DATETIME,
   end                 DATETIME,
   description         VARCHAR(255),
   public              BOOLEAN NOT NULL DEFAULT 0,
   primary key         (pet_id),
   key(scientific_name,variant,userid)
);

create table pet_notes (
   pet_id              VARCHAR(100) NOT NULL,
   public              BOOLEAN NOT NULL DEFAULT 0,
   note                TEXT,
   timestamp           TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   primary key         (pet_id,timestamp)
);

drop view itis_common_names;
create view itis_common_names 
as select v.tsn,
          v.vernacular_name,
          t.unit_name1,
          t.unit_name2,
          t.complete_name
   from ITIS.vernaculars v,
        ITIS.taxonomic_units t
   where v.tsn=t.tsn
         and t.unit_name2 != "";

drop view itis_species;
create view itis_species
as select t.tsn,
          t.unit_name1,
          t.unit_name2,
          t.complete_name
   from ITIS.taxonomic_units t

