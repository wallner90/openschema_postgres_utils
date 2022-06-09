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
-- object: postgres | type: DATABASE --
-- DROP DATABASE IF EXISTS postgres;
-- CREATE DATABASE postgres
-- 	ENCODING = 'UTF8'
-- 	LC_COLLATE = 'en_US.UTF-8'
-- 	LC_CTYPE = 'en_US.UTF-8'
-- 	TABLESPACE = pg_default
-- 	OWNER = postgres;
-- -- ddl-end --
-- COMMENT ON DATABASE postgres IS E'default administrative connection database';
-- -- ddl-end --


-- object: public.sensor | type: TABLE --
-- DROP TABLE IF EXISTS public.sensor CASCADE;
CREATE TABLE IF NOT EXISTS public.sensor (
	sensor_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	topic character varying,
	description character varying,
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
CREATE TABLE IF NOT EXISTS public.camera (
	sensor_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	camera_id character varying NOT NULL DEFAULT uuid_generate_v4(),
	camera_rig_id_camera_rig character varying,
-- 	topic character varying,
-- 	description character varying,
	CONSTRAINT camera_pk PRIMARY KEY (camera_id,sensor_id)
)
 INHERITS(public.sensor);
-- ddl-end --
ALTER TABLE public.camera OWNER TO postgres;
-- ddl-end --

-- object: public.camera_rig | type: TABLE --
-- DROP TABLE IF EXISTS public.camera_rig CASCADE;
CREATE TABLE IF NOT EXISTS public.camera_rig (
	camera_rig_id character varying NOT NULL DEFAULT uuid_generate_v4(),
	description character varying,
	CONSTRAINT camera_rig_pk PRIMARY KEY (camera_rig_id)
);
-- ddl-end --
ALTER TABLE public.camera_rig OWNER TO postgres;
-- ddl-end --

-- object: public.imu | type: TABLE --
-- DROP TABLE IF EXISTS public.imu CASCADE;
CREATE TABLE IF NOT EXISTS public.imu (
	sensor_id uuid NOT NULL DEFAULT uuid_generate_v4(),
-- 	topic character varying,
-- 	description character varying,
	CONSTRAINT imu_pk PRIMARY KEY (sensor_id)
)
 INHERITS(public.sensor);
-- ddl-end --
ALTER TABLE public.imu OWNER TO postgres;
-- ddl-end --

-- object: camera_rig_fk | type: CONSTRAINT --
-- ALTER TABLE public.camera DROP CONSTRAINT IF EXISTS camera_rig_fk CASCADE;
ALTER TABLE public.camera ADD CONSTRAINT camera_rig_fk FOREIGN KEY (camera_rig_id_camera_rig)
REFERENCES public.camera_rig (camera_rig_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: "grant_CU_eb94f049ac" | type: PERMISSION --
GRANT CREATE,USAGE
   ON SCHEMA public
   TO postgres;
-- ddl-end --

-- object: "grant_CU_cd8e46e7b6" | type: PERMISSION --
GRANT CREATE,USAGE
   ON SCHEMA public
   TO PUBLIC;
-- ddl-end --

