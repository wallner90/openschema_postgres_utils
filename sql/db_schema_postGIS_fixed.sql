-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler version: 0.9.4
-- PostgreSQL version: 13.0
-- Project Site: pgmodeler.io
-- Model Author: ---

-- Database creation must be performed outside a multi lined SQL file. 
-- These commands were put in this file only as a convenience.
-- 
-- object: "openSCHEMA_postGIS_experiments" | type: DATABASE --
-- DROP DATABASE IF EXISTS "openSCHEMA_postGIS_experiments";
-- CREATE DATABASE "openSCHEMA_postGIS_experiments";
-- ddl-end --

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS AppUser (
    id                      uuid NOT NULL DEFAULT uuid_generate_v4(),
    username                varchar (256) NOT NULL,
    email                   varchar (256) NOT NULL,
    password                varchar (256) NOT NULL,
    role                    varchar (256) NULL,
    CONSTRAINT              UK_APPUSER_USERNAME UNIQUE (username),
    CONSTRAINT              UK_APPUSER_EMAIL UNIQUE (email),
    CONSTRAINT              user_pk PRIMARY KEY (id)
);



-- object: public.sensor | type: TABLE --
-- DROP TABLE IF EXISTS public.sensor CASCADE;
CREATE TABLE public.sensor (
	sensor_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	topic varchar,
	description varchar,
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
CREATE EXTENSION IF NOT EXISTS postgis
WITH SCHEMA public;
-- ddl-end --

-- object: public.vertex | type: TABLE --
-- DROP TABLE IF EXISTS public.vertex CASCADE;
CREATE TABLE public.vertex (
	vertex_id serial NOT NULL,
	"position" geometry(POINT),
	posegraph_id_posegraph uuid,
	CONSTRAINT vertex_pk PRIMARY KEY (vertex_id)
);
-- ddl-end --
ALTER TABLE public.vertex OWNER TO postgres;
-- ddl-end --

-- object: public.camera | type: TABLE --
-- DROP TABLE IF EXISTS public.camera CASCADE;
CREATE TABLE public.camera (
	camera_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	camera_rig_id_camera_rig uuid,
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
	CONSTRAINT imu_pk PRIMARY KEY (sensor_id)
)
 INHERITS(public.sensor);
-- ddl-end --
ALTER TABLE public.imu OWNER TO postgres;
-- ddl-end --

-- object: public.edge | type: TABLE --
-- DROP TABLE IF EXISTS public.edge CASCADE;
CREATE TABLE public.edge (
	edge_id serial NOT NULL,
	"T_A_B" float[][][][][][][] DEFAULT '{1,0,0,0,0,0,0}',
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
	description varchar,
	CONSTRAINT posegraph_pk PRIMARY KEY (posegraph_id)
);
-- ddl-end --
ALTER TABLE public.posegraph OWNER TO postgres;
-- ddl-end --

-- object: posegraph_fk | type: CONSTRAINT --
-- ALTER TABLE public.sensor DROP CONSTRAINT IF EXISTS posegraph_fk CASCADE;
ALTER TABLE public.sensor ADD CONSTRAINT posegraph_fk FOREIGN KEY (posegraph_id_posegraph)
REFERENCES public.posegraph (posegraph_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: posegraph_fk | type: CONSTRAINT --
-- ALTER TABLE public.edge DROP CONSTRAINT IF EXISTS posegraph_fk CASCADE;
ALTER TABLE public.edge ADD CONSTRAINT posegraph_fk FOREIGN KEY (posegraph_id_posegraph)
REFERENCES public.posegraph (posegraph_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: posegraph_fk | type: CONSTRAINT --
-- ALTER TABLE public.vertex DROP CONSTRAINT IF EXISTS posegraph_fk CASCADE;
ALTER TABLE public.vertex ADD CONSTRAINT posegraph_fk FOREIGN KEY (posegraph_id_posegraph)
REFERENCES public.posegraph (posegraph_id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: base_sensor | type: CONSTRAINT --
-- ALTER TABLE public.posegraph DROP CONSTRAINT IF EXISTS base_sensor CASCADE;
ALTER TABLE public.posegraph ADD CONSTRAINT base_sensor FOREIGN KEY (posegraph_id)
REFERENCES public.sensor (sensor_id) MATCH SIMPLE
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --


