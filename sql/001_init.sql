CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS AppUser (
    id                      varchar (256) PRIMARY KEY,
    username                varchar (256) NOT NULL,
    email                   varchar (256) NOT NULL,
    password                varchar (256) NOT NULL,
    role                    varchar (256) NULL,
    CONSTRAINT              UK_APPUSER_USERNAME UNIQUE (username),
    CONSTRAINT              UK_APPUSER_EMAIL UNIQUE (email)
);


-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler version: 0.9.4
-- PostgreSQL version: 13.0
-- Project Site: pgmodeler.io
-- Model Author: ---

-- Database creation must be performed outside a multi lined SQL file. 
-- These commands were put in this file only as a convenience.
-- 
-- object: new_database | type: DATABASE --
-- DROP DATABASE IF EXISTS new_database;
-- CREATE DATABASE new_database;
-- ddl-end --


-- object: public.sensor | type: TABLE --
-- DROP TABLE IF EXISTS public.sensor CASCADE;
CREATE TABLE public.sensor (
	sensor_id integer NOT NULL,
	topic varchar,
	description varchar,
	CONSTRAINT sensor_pk PRIMARY KEY (sensor_id)
);
-- ddl-end --
COMMENT ON COLUMN public.sensor.topic IS E'ROS topic associated with sensor';
-- ddl-end --
COMMENT ON COLUMN public.sensor.description IS E'information about the sensor';
-- ddl-end --
ALTER TABLE public.sensor OWNER TO postgres;
-- ddl-end --

-- object: public.camera | type: TABLE --
-- DROP TABLE IF EXISTS public.camera CASCADE;
CREATE TABLE public.camera (
	camera_id integer NOT NULL,
	camera_rig_id_camera_rig integer,
-- 	sensor_id integer NOT NULL,
-- 	topic varchar,
-- 	description varchar,
	CONSTRAINT camera_pk PRIMARY KEY (camera_id,sensor_id)
)
 INHERITS(public.sensor);
-- ddl-end --
ALTER TABLE public.camera OWNER TO postgres;
-- ddl-end --

-- object: public.camera_rig | type: TABLE --
-- DROP TABLE IF EXISTS public.camera_rig CASCADE;
CREATE TABLE public.camera_rig (
	camera_rig_id integer NOT NULL,
	description varchar,
	CONSTRAINT camera_rig_pk PRIMARY KEY (camera_rig_id)
);
-- ddl-end --
ALTER TABLE public.camera_rig OWNER TO postgres;
-- ddl-end --

-- object: camera_rig_fk | type: CONSTRAINT --
-- ALTER TABLE public.camera DROP CONSTRAINT IF EXISTS camera_rig_fk CASCADE;
ALTER TABLE public.camera ADD CONSTRAINT camera_rig_fk FOREIGN KEY (camera_rig_id_camera_rig)
REFERENCES public.camera_rig (camera_rig_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: public.imu | type: TABLE --
-- DROP TABLE IF EXISTS public.imu CASCADE;
CREATE TABLE public.imu (
-- 	sensor_id integer NOT NULL,
-- 	topic varchar,
-- 	description varchar,
	CONSTRAINT imu_pk PRIMARY KEY (sensor_id)
)
 INHERITS(public.sensor);
-- ddl-end --
ALTER TABLE public.imu OWNER TO postgres;
-- ddl-end --


