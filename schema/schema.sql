
drop view itis_common_names;
create view itis_common_names 
as select v.tsn,
          v.vernacular_name,
          v.language,
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
   where t.unit_name2 != "";

