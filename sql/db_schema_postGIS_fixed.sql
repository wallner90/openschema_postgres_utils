-- -- Database generated with pgModeler (PostgreSQL Database Modeler).
-- -- pgModeler version: 0.9.4
-- -- PostgreSQL version: 13.0
-- -- Project Site: pgmodeler.io
-- -- Model Author: ---

-- -- Database creation must be performed outside a multi lined SQL file. 
-- -- These commands were put in this file only as a convenience.
-- -- 
-- -- object: postgres | type: DATABASE --
-- -- DROP DATABASE IF EXISTS postgres;
-- CREATE DATABASE postgres
-- 	ENCODING = 'UTF8'
-- 	LC_COLLATE = 'en_US.UTF-8'
-- 	LC_CTYPE = 'en_US.UTF-8'
-- 	TABLESPACE = pg_default
-- 	OWNER = postgres;
-- -- ddl-end --
-- COMMENT ON DATABASE postgres IS E'default administrative connection database';
-- -- ddl-end --


-- -- object: public.oatpp_schema_version | type: TABLE --
-- -- DROP TABLE IF EXISTS public.oatpp_schema_version CASCADE;
-- CREATE TABLE public.oatpp_schema_version (
-- 	version bigint

-- );
-- -- ddl-end --
-- ALTER TABLE public.oatpp_schema_version OWNER TO postgres;
-- -- ddl-end --

-- object: "uuid-ossp" | type: EXTENSION --
-- DROP EXTENSION IF EXISTS "uuid-ossp" CASCADE;
CREATE EXTENSION "uuid-ossp"
WITH SCHEMA public
VERSION '1.1';
-- ddl-end --
COMMENT ON EXTENSION "uuid-ossp" IS E'generate universally unique identifiers (UUIDs)';
-- ddl-end --

-- object: public.appuser | type: TABLE --
-- DROP TABLE IF EXISTS public.appuser CASCADE;
CREATE TABLE public.appuser (
	id uuid NOT NULL DEFAULT uuid_generate_v4(),
	username character varying(256) NOT NULL,
	email character varying(256) NOT NULL,
	password character varying(256) NOT NULL,
	role character varying(256),
	CONSTRAINT user_pk PRIMARY KEY (id),
	CONSTRAINT uk_appuser_username UNIQUE (username),
	CONSTRAINT uk_appuser_email UNIQUE (email)
);
-- ddl-end --
ALTER TABLE public.appuser OWNER TO postgres;
-- ddl-end --

-- object: public.sensor | type: TABLE --
-- DROP TABLE IF EXISTS public.sensor CASCADE;
CREATE TABLE public.sensor (
	sensor_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	topic character varying,
	description character varying,
	posegraph_id_posegraph uuid,
	CONSTRAINT sensor_pk PRIMARY KEY (sensor_id)
);
-- ddl-end --
COMMENT ON COLUMN public.sensor.topic IS E'ROS topic associated with sensor';
-- ddl-end --
COMMENT ON COLUMN public.sensor.description IS E'information about the sensor';
-- ddl-end --
ALTER TABLE public.sensor OWNER TO postgres;
-- ddl-end --

-- object: postgis | type: EXTENSION --
-- DROP EXTENSION IF EXISTS postgis CASCADE;
CREATE EXTENSION postgis
WITH SCHEMA public
VERSION '3.0.0';
-- ddl-end --
COMMENT ON EXTENSION postgis IS E'PostGIS geometry, geography, and raster spatial types and functions';
-- ddl-end --

-- object: public.vertex_vertex_id_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS public.vertex_vertex_id_seq CASCADE;
CREATE SEQUENCE public.vertex_vertex_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;

-- ddl-end --
ALTER SEQUENCE public.vertex_vertex_id_seq OWNER TO postgres;
-- ddl-end --

-- object: public.vertex | type: TABLE --
-- DROP TABLE IF EXISTS public.vertex CASCADE;
CREATE TABLE public.vertex (
	vertex_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	"position" geometry(POINT),
	posegraph_id_posegraph uuid,
	CONSTRAINT vertex_pk PRIMARY KEY (vertex_id)
);
-- ddl-end --
ALTER TABLE public.vertex OWNER TO postgres;
-- ddl-end --
ALTER TABLE public.vertex ENABLE ROW LEVEL SECURITY;
-- ddl-end --

-- object: public.camera | type: TABLE --
-- DROP TABLE IF EXISTS public.camera CASCADE;
CREATE TABLE public.camera (
	sensor_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	camera_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	camera_rig_id_camera_rig uuid,
-- 	topic character varying,
-- 	description character varying,
-- 	posegraph_id_posegraph uuid,
	CONSTRAINT camera_pk PRIMARY KEY (camera_id,sensor_id)
)
 INHERITS(public.sensor);
-- ddl-end --
ALTER TABLE public.camera OWNER TO postgres;
-- ddl-end --

-- object: public.camera_rig | type: TABLE --
-- DROP TABLE IF EXISTS public.camera_rig CASCADE;
CREATE TABLE public.camera_rig (
	camera_rig_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	description character varying,
	CONSTRAINT camera_rig_pk PRIMARY KEY (camera_rig_id)
);
-- ddl-end --
ALTER TABLE public.camera_rig OWNER TO postgres;
-- ddl-end --

-- object: public.imu | type: TABLE --
-- DROP TABLE IF EXISTS public.imu CASCADE;
CREATE TABLE public.imu (
	sensor_id uuid NOT NULL DEFAULT uuid_generate_v4(),
-- 	topic character varying,
-- 	description character varying,
-- 	posegraph_id_posegraph uuid,
	CONSTRAINT imu_pk PRIMARY KEY (sensor_id)
)
 INHERITS(public.sensor);
-- ddl-end --
ALTER TABLE public.imu OWNER TO postgres;
-- ddl-end --

-- object: public.edge_edge_id_seq | type: SEQUENCE --
-- DROP SEQUENCE IF EXISTS public.edge_edge_id_seq CASCADE;
CREATE SEQUENCE public.edge_edge_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START WITH 1
	CACHE 1
	NO CYCLE
	OWNED BY NONE;

-- ddl-end --
ALTER SEQUENCE public.edge_edge_id_seq OWNER TO postgres;
-- ddl-end --

-- object: public.edge | type: TABLE --
-- DROP TABLE IF EXISTS public.edge CASCADE;
CREATE TABLE public.edge (
	edge_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	"T_A_B" double precision[] DEFAULT '{1,0,0,0,0,0,0}'::double precision[],
	start_vertex public.vertex,
	end_vertex public.vertex,
	posegraph_id_posegraph uuid,
	CONSTRAINT edge_pk PRIMARY KEY (edge_id)
);
-- ddl-end --
COMMENT ON COLUMN public.edge."T_A_B" IS E'transformation between start and end vertex of edge (0:3 quaternion, 4:6 translation)';
-- ddl-end --
ALTER TABLE public.edge OWNER TO postgres;
-- ddl-end --

-- object: public.posegraph | type: TABLE --
-- DROP TABLE IF EXISTS public.posegraph CASCADE;
CREATE TABLE public.posegraph (
	posegraph_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	description character varying,
	CONSTRAINT posegraph_pk PRIMARY KEY (posegraph_id)
);
-- ddl-end --
ALTER TABLE public.posegraph OWNER TO postgres;
-- ddl-end --

-- object: public.postgis_test | type: TABLE --
-- DROP TABLE IF EXISTS public.postgis_test CASCADE;
CREATE TABLE public.postgis_test (
	id uuid NOT NULL DEFAULT uuid_generate_v4(),
	point geometry(POINT),
	CONSTRAINT postgis_test_pk PRIMARY KEY (id)
);
-- ddl-end --
ALTER TABLE public.postgis_test OWNER TO postgres;
-- ddl-end --

-- object: posegraph_fk | type: CONSTRAINT --
-- ALTER TABLE public.sensor DROP CONSTRAINT IF EXISTS posegraph_fk CASCADE;
ALTER TABLE public.sensor ADD CONSTRAINT posegraph_fk FOREIGN KEY (posegraph_id_posegraph)
REFERENCES public.posegraph (posegraph_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: posegraph_fk | type: CONSTRAINT --
-- ALTER TABLE public.vertex DROP CONSTRAINT IF EXISTS posegraph_fk CASCADE;
ALTER TABLE public.vertex ADD CONSTRAINT posegraph_fk FOREIGN KEY (posegraph_id_posegraph)
REFERENCES public.posegraph (posegraph_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: camera_rig_fk | type: CONSTRAINT --
-- ALTER TABLE public.camera DROP CONSTRAINT IF EXISTS camera_rig_fk CASCADE;
ALTER TABLE public.camera ADD CONSTRAINT camera_rig_fk FOREIGN KEY (camera_rig_id_camera_rig)
REFERENCES public.camera_rig (camera_rig_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: posegraph_fk | type: CONSTRAINT --
-- ALTER TABLE public.edge DROP CONSTRAINT IF EXISTS posegraph_fk CASCADE;
ALTER TABLE public.edge ADD CONSTRAINT posegraph_fk FOREIGN KEY (posegraph_id_posegraph)
REFERENCES public.posegraph (posegraph_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --


