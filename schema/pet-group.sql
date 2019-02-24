alter table pet_data add `group_name` varchar(50) default '' after `public`;

ALTER TABLE pet_data CHANGE COLUMN group_name group_name VARCHAR(50) not null default "";

