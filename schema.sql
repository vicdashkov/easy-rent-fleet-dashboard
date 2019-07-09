--
-- PostgreSQL database dump
--

-- Dumped from database version 11.4 (Debian 11.4-1.pgdg90+1)
-- Dumped by pg_dump version 11.3

-- Started on 2019-07-09 04:46:35 +04

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
-- TOC entry 615 (class 1247 OID 24650)
-- Name: currency; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.currency AS ENUM (
    'USD',
    'THB',
    'RUB'
);


ALTER TYPE public.currency OWNER TO postgres;

--
-- TOC entry 618 (class 1247 OID 24658)
-- Name: status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.status AS ENUM (
    'IN_PROGRESS',
    'PENDING',
    'DELETED',
    'ENDED'
);


ALTER TYPE public.status OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 201 (class 1259 OID 24619)
-- Name: vehicle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehicle (
    id integer NOT NULL,
    name character varying NOT NULL,
    mileage integer NOT NULL,
    location integer NOT NULL,
    plates character varying NOT NULL,
    notes text
);


ALTER TABLE public.vehicle OWNER TO postgres;

--
-- TOC entry 200 (class 1259 OID 24617)
-- Name: bike_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bike_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bike_id_seq OWNER TO postgres;

--
-- TOC entry 2934 (class 0 OID 0)
-- Dependencies: 200
-- Name: bike_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bike_id_seq OWNED BY public.vehicle.id;


--
-- TOC entry 203 (class 1259 OID 24635)
-- Name: customer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer (
    id integer NOT NULL,
    l_name character varying NOT NULL,
    f_name character varying NOT NULL,
    location integer NOT NULL,
    email character varying NOT NULL,
    notes text,
    phone character varying NOT NULL
);


ALTER TABLE public.customer OWNER TO postgres;

--
-- TOC entry 202 (class 1259 OID 24633)
-- Name: customer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.customer_id_seq OWNER TO postgres;

--
-- TOC entry 2935 (class 0 OID 0)
-- Dependencies: 202
-- Name: customer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customer_id_seq OWNED BY public.customer.id;


--
-- TOC entry 199 (class 1259 OID 24608)
-- Name: location; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.location (
    id integer NOT NULL,
    name character varying NOT NULL,
    address character varying NOT NULL,
    notes text
);


ALTER TABLE public.location OWNER TO postgres;

--
-- TOC entry 198 (class 1259 OID 24606)
-- Name: location_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.location_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.location_id_seq OWNER TO postgres;

--
-- TOC entry 2936 (class 0 OID 0)
-- Dependencies: 198
-- Name: location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.location_id_seq OWNED BY public.location.id;


--
-- TOC entry 205 (class 1259 OID 24667)
-- Name: order; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."order" (
    id integer NOT NULL,
    start timestamp with time zone NOT NULL,
    "end" timestamp with time zone NOT NULL,
    cus_id integer NOT NULL,
    amount money NOT NULL,
    mileage_start integer NOT NULL,
    mileage_end integer NOT NULL,
    vehicle integer NOT NULL,
    notes character varying,
    location_start integer NOT NULL,
    location_end integer NOT NULL,
    deposit money NOT NULL,
    d_currency public.currency NOT NULL,
    assign_p_up integer,
    assign_d_off integer,
    a_currency public.currency NOT NULL,
    status public.status NOT NULL
);


ALTER TABLE public."order" OWNER TO postgres;

--
-- TOC entry 204 (class 1259 OID 24665)
-- Name: order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.order_id_seq OWNER TO postgres;

--
-- TOC entry 2937 (class 0 OID 0)
-- Dependencies: 204
-- Name: order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_id_seq OWNED BY public."order".id;


--
-- TOC entry 197 (class 1259 OID 24597)
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    type smallint NOT NULL,
    l_name character varying NOT NULL,
    f_name character varying NOT NULL
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- TOC entry 196 (class 1259 OID 24595)
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO postgres;

--
-- TOC entry 2938 (class 0 OID 0)
-- Dependencies: 196
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- TOC entry 2778 (class 2604 OID 24638)
-- Name: customer id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer ALTER COLUMN id SET DEFAULT nextval('public.customer_id_seq'::regclass);


--
-- TOC entry 2776 (class 2604 OID 24611)
-- Name: location id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.location ALTER COLUMN id SET DEFAULT nextval('public.location_id_seq'::regclass);


--
-- TOC entry 2779 (class 2604 OID 24670)
-- Name: order id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."order" ALTER COLUMN id SET DEFAULT nextval('public.order_id_seq'::regclass);


--
-- TOC entry 2775 (class 2604 OID 24600)
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- TOC entry 2777 (class 2604 OID 24622)
-- Name: vehicle id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle ALTER COLUMN id SET DEFAULT nextval('public.bike_id_seq'::regclass);


--
-- TOC entry 2939 (class 0 OID 0)
-- Dependencies: 200
-- Name: bike_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bike_id_seq', 7, true);


--
-- TOC entry 2940 (class 0 OID 0)
-- Dependencies: 202
-- Name: customer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customer_id_seq', 5, true);


--
-- TOC entry 2941 (class 0 OID 0)
-- Dependencies: 198
-- Name: location_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.location_id_seq', 4, true);


--
-- TOC entry 2942 (class 0 OID 0)
-- Dependencies: 204
-- Name: order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_id_seq', 9, true);


--
-- TOC entry 2943 (class 0 OID 0)
-- Dependencies: 196
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_id_seq', 2, true);


--
-- TOC entry 2785 (class 2606 OID 24627)
-- Name: vehicle bike_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT bike_pkey PRIMARY KEY (id);


--
-- TOC entry 2787 (class 2606 OID 24643)
-- Name: customer customer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer
    ADD CONSTRAINT customer_pkey PRIMARY KEY (id);


--
-- TOC entry 2783 (class 2606 OID 24616)
-- Name: location location_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);


--
-- TOC entry 2789 (class 2606 OID 24675)
-- Name: order order_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pkey PRIMARY KEY (id);


--
-- TOC entry 2781 (class 2606 OID 24605)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- TOC entry 2792 (class 2606 OID 24676)
-- Name: order bike; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT bike FOREIGN KEY (vehicle) REFERENCES public.vehicle(id);


--
-- TOC entry 2793 (class 2606 OID 24681)
-- Name: order cus; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT cus FOREIGN KEY (cus_id) REFERENCES public.customer(id);


--
-- TOC entry 2791 (class 2606 OID 24644)
-- Name: customer loc; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer
    ADD CONSTRAINT loc FOREIGN KEY (location) REFERENCES public.location(id);


--
-- TOC entry 2794 (class 2606 OID 24686)
-- Name: order loc_e; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT loc_e FOREIGN KEY (location_end) REFERENCES public.location(id);


--
-- TOC entry 2795 (class 2606 OID 24691)
-- Name: order loc_s; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT loc_s FOREIGN KEY (location_start) REFERENCES public.location(id);


--
-- TOC entry 2790 (class 2606 OID 24628)
-- Name: vehicle location; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT location FOREIGN KEY (location) REFERENCES public.location(id);


--
-- TOC entry 2796 (class 2606 OID 24696)
-- Name: order user_d_off; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT user_d_off FOREIGN KEY (assign_d_off) REFERENCES public."user"(id);


--
-- TOC entry 2797 (class 2606 OID 24701)
-- Name: order user_p_up; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT user_p_up FOREIGN KEY (assign_p_up) REFERENCES public."user"(id);


-- Completed on 2019-07-09 04:46:35 +04

--
-- PostgreSQL database dump complete
--

