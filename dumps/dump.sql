--
-- PostgreSQL database dump
--

\restrict OtMMxeJb9ghzezYnrkaBwgONN50hAxQPgoahw6tNlJV7081T9qfvatwDdxscYOu

-- Dumped from database version 17.10
-- Dumped by pg_dump version 17.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_role_id_fkey;
ALTER TABLE IF EXISTS ONLY public.restaurant_managers DROP CONSTRAINT IF EXISTS restaurant_managers_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.restaurant_managers DROP CONSTRAINT IF EXISTS restaurant_managers_food_place_id_fkey;
ALTER TABLE IF EXISTS ONLY public.reservations DROP CONSTRAINT IF EXISTS reservations_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.reservations DROP CONSTRAINT IF EXISTS reservations_food_table_id_fkey;
ALTER TABLE IF EXISTS ONLY public.ratings DROP CONSTRAINT IF EXISTS ratings_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.ratings DROP CONSTRAINT IF EXISTS ratings_food_place_id_fkey;
ALTER TABLE IF EXISTS ONLY public.menu_items DROP CONSTRAINT IF EXISTS menu_items_food_place_id_fkey;
ALTER TABLE IF EXISTS ONLY public.food_tables DROP CONSTRAINT IF EXISTS food_tables_food_place_id_fkey;
ALTER TABLE IF EXISTS ONLY public.food_places DROP CONSTRAINT IF EXISTS food_places_location_id_fkey;
ALTER TABLE IF EXISTS ONLY public.food_baskets DROP CONSTRAINT IF EXISTS food_baskets_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.food_baskets DROP CONSTRAINT IF EXISTS food_baskets_food_place_id_fkey;
ALTER TABLE IF EXISTS ONLY public.basket_items DROP CONSTRAINT IF EXISTS basket_items_menu_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.basket_items DROP CONSTRAINT IF EXISTS basket_items_food_basket_id_fkey;
DROP INDEX IF EXISTS public.user_id_is_ordered_index;
DROP INDEX IF EXISTS public.ix_food_baskets_user_id;
DROP INDEX IF EXISTS public.ix_basket_items_food_basket_id;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_name_key;
ALTER TABLE IF EXISTS ONLY public.ratings DROP CONSTRAINT IF EXISTS unique_user_food_place_rating;
ALTER TABLE IF EXISTS ONLY public.food_tables DROP CONSTRAINT IF EXISTS unique_table_number_per_food_place_id;
ALTER TABLE IF EXISTS ONLY public.menu_items DROP CONSTRAINT IF EXISTS unique_name_with_food_place_id;
ALTER TABLE IF EXISTS ONLY public.food_places DROP CONSTRAINT IF EXISTS unique_name_per_location_id_and_address;
ALTER TABLE IF EXISTS ONLY public.roles DROP CONSTRAINT IF EXISTS roles_pkey;
ALTER TABLE IF EXISTS ONLY public.roles DROP CONSTRAINT IF EXISTS roles_name_key;
ALTER TABLE IF EXISTS ONLY public.restaurant_managers DROP CONSTRAINT IF EXISTS restaurant_managers_pkey;
ALTER TABLE IF EXISTS ONLY public.reservations DROP CONSTRAINT IF EXISTS reservations_pkey;
ALTER TABLE IF EXISTS ONLY public.ratings DROP CONSTRAINT IF EXISTS ratings_pkey;
ALTER TABLE IF EXISTS ONLY public.menu_items DROP CONSTRAINT IF EXISTS menu_items_pkey;
ALTER TABLE IF EXISTS ONLY public.locations DROP CONSTRAINT IF EXISTS locations_pkey;
ALTER TABLE IF EXISTS ONLY public.locations DROP CONSTRAINT IF EXISTS locations_name_key;
ALTER TABLE IF EXISTS ONLY public.food_tables DROP CONSTRAINT IF EXISTS food_tables_pkey;
ALTER TABLE IF EXISTS ONLY public.food_places DROP CONSTRAINT IF EXISTS food_places_pkey;
ALTER TABLE IF EXISTS ONLY public.food_baskets DROP CONSTRAINT IF EXISTS food_baskets_pkey;
ALTER TABLE IF EXISTS ONLY public.basket_items DROP CONSTRAINT IF EXISTS basket_items_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.roles ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.reservations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.ratings ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.menu_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.locations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.food_tables ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.food_places ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.food_baskets ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.basket_items ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.roles_id_seq;
DROP TABLE IF EXISTS public.roles;
DROP TABLE IF EXISTS public.restaurant_managers;
DROP SEQUENCE IF EXISTS public.reservations_id_seq;
DROP TABLE IF EXISTS public.reservations;
DROP SEQUENCE IF EXISTS public.ratings_id_seq;
DROP TABLE IF EXISTS public.ratings;
DROP SEQUENCE IF EXISTS public.menu_items_id_seq;
DROP TABLE IF EXISTS public.menu_items;
DROP SEQUENCE IF EXISTS public.locations_id_seq;
DROP TABLE IF EXISTS public.locations;
DROP SEQUENCE IF EXISTS public.food_tables_id_seq;
DROP TABLE IF EXISTS public.food_tables;
DROP SEQUENCE IF EXISTS public.food_places_id_seq;
DROP TABLE IF EXISTS public.food_places;
DROP SEQUENCE IF EXISTS public.food_baskets_id_seq;
DROP TABLE IF EXISTS public.food_baskets;
DROP SEQUENCE IF EXISTS public.basket_items_id_seq;
DROP TABLE IF EXISTS public.basket_items;
DROP TABLE IF EXISTS public.alembic_version;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: basket_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.basket_items (
    id integer NOT NULL,
    item_quantity integer NOT NULL,
    menu_item_id integer NOT NULL,
    food_basket_id integer NOT NULL
);


ALTER TABLE public.basket_items OWNER TO postgres;

--
-- Name: basket_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.basket_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.basket_items_id_seq OWNER TO postgres;

--
-- Name: basket_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.basket_items_id_seq OWNED BY public.basket_items.id;


--
-- Name: food_baskets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.food_baskets (
    id integer NOT NULL,
    ordered_at timestamp without time zone,
    is_ordered boolean NOT NULL,
    user_id integer NOT NULL,
    food_place_id integer NOT NULL,
    order_type character varying,
    phone character varying,
    address character varying,
    status character varying NOT NULL,
    delivery_time time without time zone
);


ALTER TABLE public.food_baskets OWNER TO postgres;

--
-- Name: food_baskets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.food_baskets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.food_baskets_id_seq OWNER TO postgres;

--
-- Name: food_baskets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.food_baskets_id_seq OWNED BY public.food_baskets.id;


--
-- Name: food_places; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.food_places (
    id integer NOT NULL,
    name character varying NOT NULL,
    address character varying NOT NULL,
    description character varying,
    open_time time without time zone NOT NULL,
    close_time time without time zone NOT NULL,
    location_id integer NOT NULL,
    image_path character varying
);


ALTER TABLE public.food_places OWNER TO postgres;

--
-- Name: food_places_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.food_places_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.food_places_id_seq OWNER TO postgres;

--
-- Name: food_places_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.food_places_id_seq OWNED BY public.food_places.id;


--
-- Name: food_tables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.food_tables (
    id integer NOT NULL,
    table_number character varying NOT NULL,
    max_seats integer NOT NULL,
    food_place_id integer NOT NULL
);


ALTER TABLE public.food_tables OWNER TO postgres;

--
-- Name: food_tables_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.food_tables_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.food_tables_id_seq OWNER TO postgres;

--
-- Name: food_tables_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.food_tables_id_seq OWNED BY public.food_tables.id;


--
-- Name: locations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.locations (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.locations OWNER TO postgres;

--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.locations_id_seq OWNER TO postgres;

--
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;


--
-- Name: menu_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.menu_items (
    id integer NOT NULL,
    name character varying NOT NULL,
    price numeric(10,2) NOT NULL,
    description character varying,
    food_place_id integer NOT NULL,
    image_path character varying,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.menu_items OWNER TO postgres;

--
-- Name: menu_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.menu_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.menu_items_id_seq OWNER TO postgres;

--
-- Name: menu_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.menu_items_id_seq OWNED BY public.menu_items.id;


--
-- Name: ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ratings (
    id integer NOT NULL,
    score integer NOT NULL,
    user_id integer NOT NULL,
    food_place_id integer NOT NULL,
    CONSTRAINT check_score_range CHECK (((1 <= score) AND (score <= 5)))
);


ALTER TABLE public.ratings OWNER TO postgres;

--
-- Name: ratings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ratings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ratings_id_seq OWNER TO postgres;

--
-- Name: ratings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ratings_id_seq OWNED BY public.ratings.id;


--
-- Name: reservations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservations (
    id integer NOT NULL,
    start_datetime timestamp without time zone NOT NULL,
    duration_in_minutes integer NOT NULL,
    user_id integer NOT NULL,
    food_table_id integer NOT NULL
);


ALTER TABLE public.reservations OWNER TO postgres;

--
-- Name: reservations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservations_id_seq OWNER TO postgres;

--
-- Name: reservations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservations_id_seq OWNED BY public.reservations.id;


--
-- Name: restaurant_managers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.restaurant_managers (
    user_id integer NOT NULL,
    food_place_id integer NOT NULL
);


ALTER TABLE public.restaurant_managers OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(32) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    hashed_password character varying NOT NULL,
    is_active boolean NOT NULL,
    role_id integer,
    phone character varying(32)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: basket_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.basket_items ALTER COLUMN id SET DEFAULT nextval('public.basket_items_id_seq'::regclass);


--
-- Name: food_baskets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_baskets ALTER COLUMN id SET DEFAULT nextval('public.food_baskets_id_seq'::regclass);


--
-- Name: food_places id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_places ALTER COLUMN id SET DEFAULT nextval('public.food_places_id_seq'::regclass);


--
-- Name: food_tables id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_tables ALTER COLUMN id SET DEFAULT nextval('public.food_tables_id_seq'::regclass);


--
-- Name: locations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);


--
-- Name: menu_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items ALTER COLUMN id SET DEFAULT nextval('public.menu_items_id_seq'::regclass);


--
-- Name: ratings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings ALTER COLUMN id SET DEFAULT nextval('public.ratings_id_seq'::regclass);


--
-- Name: reservations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations ALTER COLUMN id SET DEFAULT nextval('public.reservations_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
f0ca41960823
\.


--
-- Data for Name: basket_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.basket_items (id, item_quantity, menu_item_id, food_basket_id) FROM stdin;
16	1	13	6
17	2	17	6
18	2	14	7
19	1	16	7
20	5	13	8
21	3	14	8
22	1	15	8
23	1	14	9
\.


--
-- Data for Name: food_baskets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.food_baskets (id, ordered_at, is_ordered, user_id, food_place_id, order_type, phone, address, status, delivery_time) FROM stdin;
6	2026-06-04 12:15:00	t	15	4	dinein	+7 (911) 234-56-78	\N	preparing	\N
8	\N	f	20	4	dinein	\N	\N	new	\N
9	\N	f	19	4	dinein	\N	\N	new	\N
7	2026-06-04 13:45:00	t	17	4	delivery	+7 (999) 888-77-66	ул. Петровка, д. 10, кв. 42	new	\N
\.


--
-- Data for Name: food_places; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.food_places (id, name, address, description, open_time, close_time, location_id, image_path) FROM stdin;
4	La Bottega	ул. Петровка, 12	Итальянская кухня	12:00:00	23:00:00	5	\N
5	Sakura Palace	Пресненская наб., 8	Японская кухня	12:00:00	23:00:00	5	\N
6	Северный Модерн	Невский пр., 28	Русская кухня	12:00:00	23:00:00	6	\N
\.


--
-- Data for Name: food_tables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.food_tables (id, table_number, max_seats, food_place_id) FROM stdin;
17	1	2	4
18	2	4	4
19	3	2	4
20	4	6	4
21	5	4	4
22	6	2	4
23	7	8	4
24	8	4	4
25	1	2	5
26	2	2	5
27	3	4	5
28	4	4	5
29	5	6	5
30	1	4	6
31	2	6	6
32	3	2	6
\.


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.locations (id, name) FROM stdin;
5	Москва
6	Санкт-Петербург
7	Краснодар
8	Сочи
\.


--
-- Data for Name: menu_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.menu_items (id, name, price, description, food_place_id, image_path, is_active) FROM stdin;
13	Пицца Маргарита	650.00	Томатный соус, моцарелла, базилик, оливковое масло	4	\N	t
14	Паста Карбонара	790.00	Спагетти, гуанчиале, яичный желток, пекорино романо	4	\N	t
15	Флорентийский стейк	2400.00	Сочный стейк Рибай из мраморной говядины на гриле	4	\N	t
16	Тирамису Классик	420.00	Маскарпоне, савоярди, кофе эспрессо, какао-порошок	4	\N	t
17	Лимонад Базилик	350.00	Свежий базилик, сок лимона, содовая, тростниковый сахар	4	\N	t
18	Сет Нигири Премиум	1850.00	Лосось, тунец, угорь, креветка, морской гребешок	5	\N	t
19	Ролл Филадельфия	820.00	Лосось, сливочный сыр, огурец, икра тобико	5	\N	t
20	Суп Рамен с уткой	690.00	Утиная грудка, пшеничная лапша, яйцо аджитама, бульон	5	\N	t
21	Моти Ассорти	450.00	Японские пирожные с матчей, манго и клубникой	5	\N	t
22	Чай Сентя	300.00	Традиционный японский зеленый чай из листьев нового урожая	5	\N	t
23	Блины с красной икрой	950.00	Тонкие пшеничные блины, красная икра, фермерская сметана	6	\N	t
24	Бефстроганов	1100.00	Вырезка говяжья, лесные грибы, картофельное пюре	6	\N	t
\.


--
-- Data for Name: ratings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ratings (id, score, user_id, food_place_id) FROM stdin;
\.


--
-- Data for Name: reservations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reservations (id, start_datetime, duration_in_minutes, user_id, food_table_id) FROM stdin;
2	2026-06-04 19:00:00	120	16	18
3	2026-06-14 16:00:00	120	20	21
\.


--
-- Data for Name: restaurant_managers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.restaurant_managers (user_id, food_place_id) FROM stdin;
18	4
18	5
21	4
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name) FROM stdin;
1	client
2	manager
3	admin
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, name, hashed_password, is_active, role_id, phone) FROM stdin;
14	ivanov	$2b$12$.AEtw0O5/KssQtzwvc0s9OX2MPVTG5QGOJvoNYPEqLZd20Cv3zRGu	t	1	\N
16	Мария Смирнова	$2b$12$1TPFOjq5CZH6YI9CStXhtuTiYLU.YKPGhiVg6ueWe7nX1m2kyPt/W	t	1	\N
17	Дмитрий Петров	$2b$12$fvnK9kaYpezO6nU1VVZlreuHvQGG0fFFVH7Qjiom6isWbzyu55AGi	t	1	\N
18	smirnov_manager	$2b$12$JK8E/o2Mw6VvdM3mWx2SGu9dc8E.zKKzGJMJBYUHYLhCe.tSLICl2	t	2	\N
20	chupik	$2b$12$abqUEOkvZ583MgM8U7TThOB4y1c0Mv5OZ0pi0lC5tbkbWUVhzNf.q	t	1	\N
15	Алексей Иванов	$2b$12$vOl501hzRyIxXSAhX0w.o.O0JVhww7tV1aeYvYvT.nP0AWv4CZQJi	t	1	+7 (911) 234-56-78
21	chpdd	$2b$12$/jsxZgYS18E9/9xGVxX2refwcQeP1Vq99L9dgKHsW2GU7gScw4QXu	t	2	891812343212323
19	admin	$2b$12$hWce5HtQnZ9Kfr66aIWbsOWz5O.qUT4rSxCzbs63PafIlGV2CDgQG	t	3	89189640998
\.


--
-- Name: basket_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.basket_items_id_seq', 23, true);


--
-- Name: food_baskets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.food_baskets_id_seq', 9, true);


--
-- Name: food_places_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.food_places_id_seq', 6, true);


--
-- Name: food_tables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.food_tables_id_seq', 32, true);


--
-- Name: locations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.locations_id_seq', 8, true);


--
-- Name: menu_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.menu_items_id_seq', 24, true);


--
-- Name: ratings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ratings_id_seq', 3, true);


--
-- Name: reservations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reservations_id_seq', 3, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 3, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 21, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: basket_items basket_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.basket_items
    ADD CONSTRAINT basket_items_pkey PRIMARY KEY (id);


--
-- Name: food_baskets food_baskets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_baskets
    ADD CONSTRAINT food_baskets_pkey PRIMARY KEY (id);


--
-- Name: food_places food_places_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_places
    ADD CONSTRAINT food_places_pkey PRIMARY KEY (id);


--
-- Name: food_tables food_tables_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_tables
    ADD CONSTRAINT food_tables_pkey PRIMARY KEY (id);


--
-- Name: locations locations_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_name_key UNIQUE (name);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: menu_items menu_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items
    ADD CONSTRAINT menu_items_pkey PRIMARY KEY (id);


--
-- Name: ratings ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_pkey PRIMARY KEY (id);


--
-- Name: reservations reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_pkey PRIMARY KEY (id);


--
-- Name: restaurant_managers restaurant_managers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurant_managers
    ADD CONSTRAINT restaurant_managers_pkey PRIMARY KEY (user_id, food_place_id);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: food_places unique_name_per_location_id_and_address; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_places
    ADD CONSTRAINT unique_name_per_location_id_and_address UNIQUE (name, location_id, address);


--
-- Name: menu_items unique_name_with_food_place_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items
    ADD CONSTRAINT unique_name_with_food_place_id UNIQUE (name, food_place_id);


--
-- Name: food_tables unique_table_number_per_food_place_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_tables
    ADD CONSTRAINT unique_table_number_per_food_place_id UNIQUE (table_number, food_place_id);


--
-- Name: ratings unique_user_food_place_rating; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT unique_user_food_place_rating UNIQUE (user_id, food_place_id);


--
-- Name: users users_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_name_key UNIQUE (name);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_basket_items_food_basket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_basket_items_food_basket_id ON public.basket_items USING btree (food_basket_id);


--
-- Name: ix_food_baskets_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_food_baskets_user_id ON public.food_baskets USING btree (user_id);


--
-- Name: user_id_is_ordered_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_id_is_ordered_index ON public.food_baskets USING btree (user_id, is_ordered);


--
-- Name: basket_items basket_items_food_basket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.basket_items
    ADD CONSTRAINT basket_items_food_basket_id_fkey FOREIGN KEY (food_basket_id) REFERENCES public.food_baskets(id) ON DELETE CASCADE;


--
-- Name: basket_items basket_items_menu_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.basket_items
    ADD CONSTRAINT basket_items_menu_item_id_fkey FOREIGN KEY (menu_item_id) REFERENCES public.menu_items(id) ON DELETE CASCADE;


--
-- Name: food_baskets food_baskets_food_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_baskets
    ADD CONSTRAINT food_baskets_food_place_id_fkey FOREIGN KEY (food_place_id) REFERENCES public.food_places(id) ON DELETE CASCADE;


--
-- Name: food_baskets food_baskets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_baskets
    ADD CONSTRAINT food_baskets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: food_places food_places_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_places
    ADD CONSTRAINT food_places_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: food_tables food_tables_food_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.food_tables
    ADD CONSTRAINT food_tables_food_place_id_fkey FOREIGN KEY (food_place_id) REFERENCES public.food_places(id) ON DELETE CASCADE;


--
-- Name: menu_items menu_items_food_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items
    ADD CONSTRAINT menu_items_food_place_id_fkey FOREIGN KEY (food_place_id) REFERENCES public.food_places(id) ON DELETE CASCADE;


--
-- Name: ratings ratings_food_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_food_place_id_fkey FOREIGN KEY (food_place_id) REFERENCES public.food_places(id) ON DELETE CASCADE;


--
-- Name: ratings ratings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: reservations reservations_food_table_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_food_table_id_fkey FOREIGN KEY (food_table_id) REFERENCES public.food_tables(id) ON DELETE CASCADE;


--
-- Name: reservations reservations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: restaurant_managers restaurant_managers_food_place_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurant_managers
    ADD CONSTRAINT restaurant_managers_food_place_id_fkey FOREIGN KEY (food_place_id) REFERENCES public.food_places(id) ON DELETE CASCADE;


--
-- Name: restaurant_managers restaurant_managers_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurant_managers
    ADD CONSTRAINT restaurant_managers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- PostgreSQL database dump complete
--

\unrestrict OtMMxeJb9ghzezYnrkaBwgONN50hAxQPgoahw6tNlJV7081T9qfvatwDdxscYOu

