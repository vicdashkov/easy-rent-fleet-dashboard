-- Table: public.bike
-- DROP TABLE public.bike;
CREATE TABLE public.bike
(
    id integer NOT NULL DEFAULT nextval('bike_id_seq'::regclass),
    name character varying COLLATE pg_catalog."default" NOT NULL,
    milage integer NOT NULL,
    location integer NOT NULL,
    plates character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT bike_pkey PRIMARY KEY (id),
    CONSTRAINT location FOREIGN KEY (location)
        REFERENCES public.location (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.bike
    OWNER to postgres;

-- Table: public.customer
-- DROP TABLE public.customer;
CREATE TABLE public.customer
(
    id integer NOT NULL DEFAULT nextval('customer_id_seq'::regclass),
    l_name character varying COLLATE pg_catalog."default" NOT NULL,
    f_name character varying COLLATE pg_catalog."default" NOT NULL,
    location integer NOT NULL,
    email character varying COLLATE pg_catalog."default" NOT NULL,
    notes text COLLATE pg_catalog."default",
    phone character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT customer_pkey PRIMARY KEY (id),
    CONSTRAINT loc FOREIGN KEY (location)
        REFERENCES public.location (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.customer
    OWNER to postgres;

-- Table: public."order"
-- DROP TABLE public."order";
CREATE TABLE public."order"
(
    id integer NOT NULL DEFAULT nextval('order_id_seq'::regclass),
    start timestamp with time zone NOT NULL,
    "end" timestamp with time zone NOT NULL,
    cus_id integer NOT NULL,
    ammount money NOT NULL,
    milage_start integer NOT NULL,
    milage_end integer NOT NULL,
    bike integer NOT NULL,
    notes character varying COLLATE pg_catalog."default",
    location_start integer NOT NULL,
    location_end integer NOT NULL,
    deposit money NOT NULL,
    currency currency NOT NULL,
    assign_p_up integer NOT NULL,
    assign_d_off integer NOT NULL,
    CONSTRAINT order_pkey PRIMARY KEY (id),
    CONSTRAINT bike FOREIGN KEY (bike)
        REFERENCES public.bike (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT cus FOREIGN KEY (cus_id)
        REFERENCES public.customer (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT loc_e FOREIGN KEY (location_end)
        REFERENCES public.location (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT loc_s FOREIGN KEY (location_start)
        REFERENCES public.location (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT user_d_off FOREIGN KEY (assign_d_off)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT user_p_up FOREIGN KEY (assign_p_up)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."order"
    OWNER to postgres;

-- Table: public.location
-- DROP TABLE public.location;
CREATE TABLE public.location
(
    id integer NOT NULL DEFAULT nextval('location_id_seq'::regclass),
    name character varying COLLATE pg_catalog."default" NOT NULL,
    address character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT location_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.location
    OWNER to postgres;

-- Table: public."user"
-- DROP TABLE public."user";
CREATE TABLE public."user"
(
    id integer NOT NULL DEFAULT nextval('user_id_seq'::regclass),
    type smallint NOT NULL,
    l_name character varying COLLATE pg_catalog."default" NOT NULL,
    f_name character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."user"
    OWNER to postgres;