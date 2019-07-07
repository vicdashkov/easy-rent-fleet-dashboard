-- todo: delete this file
CREATE TABLE public.bike
(
    id serial NOT NULL,
    name character varying COLLATE pg_catalog."default" NOT NULL,
    mileage integer NOT NULL,
    location integer NOT NULL,
    plates character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT bike_pkey PRIMARY KEY (id),
    CONSTRAINT location FOREIGN KEY (location)
        REFERENCES public.location (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

CREATE TABLE public.customer
(
    id serial,
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

CREATE TABLE public."order"
(
    id serial,
    start timestamp with time zone NOT NULL,
    "end" timestamp with time zone NOT NULL,
    cus_id integer NOT NULL,
    amount money NOT NULL,
    mileage_start integer NOT NULL,
    mileage_end integer NOT NULL,
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

CREATE TABLE public.location
(
    id serial,
    name character varying COLLATE pg_catalog."default" NOT NULL,
    address character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT location_pkey PRIMARY KEY (id)
)

CREATE TABLE public."user"
(
    id serial,
    type smallint NOT NULL,
    l_name character varying COLLATE pg_catalog."default" NOT NULL,
    f_name character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (id)
)

CREATE TYPE public.currency AS ENUM
    ('USD', 'THB', 'RUB');

CREATE TYPE public.status AS ENUM
    ('IN_PROGRESS', 'PENDING', 'DELETED');

ALTER TABLE public."order"
    RENAME currency TO d_currency;

ALTER TABLE public."order"
    ADD COLUMN a_currency currency NOT NULL;

ALTER TABLE public."order"
    ADD COLUMN status status NOT NULL;

ALTER TABLE public.bike
    ADD COLUMN notes text;

ALTER TABLE public.location
    ADD COLUMN notes text;