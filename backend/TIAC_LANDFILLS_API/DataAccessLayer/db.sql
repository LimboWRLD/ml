--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

-- Started on 2025-10-20 00:58:03

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 9 (class 2615 OID 22211)
-- Name: topology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA IF NOT EXISTS topology;


ALTER SCHEMA topology OWNER TO postgres;

--
-- TOC entry 6032 (class 0 OID 0)
-- Dependencies: 9
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- TOC entry 2 (class 3079 OID 21131)
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- TOC entry 6033 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- TOC entry 4 (class 3079 OID 22381)
-- Name: postgis_sfcgal; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_sfcgal WITH SCHEMA public;


--
-- TOC entry 6034 (class 0 OID 0)
-- Dependencies: 4
-- Name: EXTENSION postgis_sfcgal; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_sfcgal IS 'PostGIS SFCGAL functions';


--
-- TOC entry 3 (class 3079 OID 22212)
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- TOC entry 6035 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


--
-- TOC entry 1820 (class 1247 OID 22444)
-- Name: landfill_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.landfill_status AS ENUM (
    'Active',
    'Inactive',
    'Closed',
    'Unknown'
);


ALTER TYPE public.landfill_status OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 233 (class 1259 OID 22454)
-- Name: landfills; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.landfills (
    id integer NOT NULL,
    landfill_id character varying(50) NOT NULL,
    status public.landfill_status NOT NULL,
    location public.geometry(Point,4326) NOT NULL,
    area_m2 real,
    volume_m3 real,
    waste_mass_tons real,
    start_year integer,
    methane_tons_per_year real,
    co2eq_tons_per_year real,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.landfills OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 22453)
-- Name: landfills_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.landfills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.landfills_id_seq OWNER TO postgres;

--
-- TOC entry 6036 (class 0 OID 0)
-- Dependencies: 232
-- Name: landfills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.landfills_id_seq OWNED BY public.landfills.id;


--
-- TOC entry 5859 (class 2604 OID 22457)
-- Name: landfills id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.landfills ALTER COLUMN id SET DEFAULT nextval('public.landfills_id_seq'::regclass);


--
-- TOC entry 6026 (class 0 OID 22454)
-- Dependencies: 233
-- Data for Name: landfills; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.landfills (id, landfill_id, status, location, area_m2, volume_m3, waste_mass_tons, start_year, methane_tons_per_year, co2eq_tons_per_year, created_at) FROM stdin;
\.


--
-- TOC entry 5852 (class 0 OID 21453)
-- Dependencies: 222
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- TOC entry 5854 (class 0 OID 22214)
-- Dependencies: 227
-- Data for Name: topology; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.topology (id, name, srid, "precision", hasz) FROM stdin;
\.


--
-- TOC entry 5855 (class 0 OID 22226)
-- Dependencies: 228
-- Data for Name: layer; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.layer (topology_id, layer_id, schema_name, table_name, feature_column, feature_type, level, child_id) FROM stdin;
\.


--
-- TOC entry 6037 (class 0 OID 0)
-- Dependencies: 232
-- Name: landfills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.landfills_id_seq', 1, false);


--
-- TOC entry 6038 (class 0 OID 0)
-- Dependencies: 226
-- Name: topology_id_seq; Type: SEQUENCE SET; Schema: topology; Owner: postgres
--

SELECT pg_catalog.setval('topology.topology_id_seq', 1, false);


--
-- TOC entry 5874 (class 2606 OID 22462)
-- Name: landfills landfills_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.landfills
    ADD CONSTRAINT landfills_pkey PRIMARY KEY (id);


--
-- TOC entry 5872 (class 1259 OID 22463)
-- Name: idx_landfills_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_landfills_location ON public.landfills USING gist (location);


-- Completed on 2025-10-20 00:58:04

--
-- PostgreSQL database dump complete
--

