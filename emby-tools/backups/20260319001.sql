--
-- PostgreSQL database dump
--

\restrict Ln7gnfExaQfVL8m186Xt3RD5fY9CPXzmFXhcFnX80qFSmiQoTsAcaT4hLmfWeL5

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

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
-- Name: taskstatus; Type: TYPE; Schema: public; Owner: emby
--

CREATE TYPE public.taskstatus AS ENUM (
    'queued',
    'running',
    'success',
    'failed',
    'cancelled'
);


ALTER TYPE public.taskstatus OWNER TO emby;

--
-- Name: tasktype; Type: TYPE; Schema: public; Owner: emby
--

CREATE TYPE public.tasktype AS ENUM (
    'tg_message',
    'transfer',
    'organize',
    'strm',
    'emby_refresh'
);


ALTER TYPE public.tasktype OWNER TO emby;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: kv_settings; Type: TABLE; Schema: public; Owner: emby
--

CREATE TABLE public.kv_settings (
    key character varying(64) NOT NULL,
    value text NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.kv_settings OWNER TO emby;

--
-- Name: library_snapshots; Type: TABLE; Schema: public; Owner: emby
--

CREATE TABLE public.library_snapshots (
    id integer NOT NULL,
    day character varying(10) NOT NULL,
    total_items integer NOT NULL,
    created_items integer NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    delta_items integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.library_snapshots OWNER TO emby;

--
-- Name: library_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: emby
--

CREATE SEQUENCE public.library_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.library_snapshots_id_seq OWNER TO emby;

--
-- Name: library_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emby
--

ALTER SEQUENCE public.library_snapshots_id_seq OWNED BY public.library_snapshots.id;


--
-- Name: pipeline_task_logs; Type: TABLE; Schema: public; Owner: emby
--

CREATE TABLE public.pipeline_task_logs (
    id integer NOT NULL,
    task_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    level character varying(16) NOT NULL,
    message text NOT NULL
);


ALTER TABLE public.pipeline_task_logs OWNER TO emby;

--
-- Name: pipeline_task_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: emby
--

CREATE SEQUENCE public.pipeline_task_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pipeline_task_logs_id_seq OWNER TO emby;

--
-- Name: pipeline_task_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emby
--

ALTER SEQUENCE public.pipeline_task_logs_id_seq OWNED BY public.pipeline_task_logs.id;


--
-- Name: pipeline_tasks; Type: TABLE; Schema: public; Owner: emby
--

CREATE TABLE public.pipeline_tasks (
    id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    type public.tasktype NOT NULL,
    status public.taskstatus NOT NULL,
    title character varying(255) NOT NULL,
    payload_json text NOT NULL
);


ALTER TABLE public.pipeline_tasks OWNER TO emby;

--
-- Name: pipeline_tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: emby
--

CREATE SEQUENCE public.pipeline_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pipeline_tasks_id_seq OWNER TO emby;

--
-- Name: pipeline_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: emby
--

ALTER SEQUENCE public.pipeline_tasks_id_seq OWNED BY public.pipeline_tasks.id;


--
-- Name: library_snapshots id; Type: DEFAULT; Schema: public; Owner: emby
--

ALTER TABLE ONLY public.library_snapshots ALTER COLUMN id SET DEFAULT nextval('public.library_snapshots_id_seq'::regclass);


--
-- Name: pipeline_task_logs id; Type: DEFAULT; Schema: public; Owner: emby
--

ALTER TABLE ONLY public.pipeline_task_logs ALTER COLUMN id SET DEFAULT nextval('public.pipeline_task_logs_id_seq'::regclass);


--
-- Name: pipeline_tasks id; Type: DEFAULT; Schema: public; Owner: emby
--

ALTER TABLE ONLY public.pipeline_tasks ALTER COLUMN id SET DEFAULT nextval('public.pipeline_tasks_id_seq'::regclass);


--
-- Data for Name: kv_settings; Type: TABLE DATA; Schema: public; Owner: emby
--

COPY public.kv_settings (key, value, updated_at) FROM stdin;
emby_base_url	http://899215.xyz:8096	2026-03-19 11:42:00.321986+08
emby_api_key	7257797bfa9d49a99fffe61ccef75852	2026-03-19 11:42:00.330533+08
settings_updated_at	2026-03-19T03:42:00.333993+00:00	2026-03-19 11:42:00.334012+08
app_password	Cui123456	2026-03-19 12:17:56.305418+08
\.


--
-- Data for Name: library_snapshots; Type: TABLE DATA; Schema: public; Owner: emby
--

COPY public.library_snapshots (id, day, total_items, created_items, updated_at, delta_items) FROM stdin;
1	2026-03-19	7647	0	2026-03-19 11:52:23.122263+08	7647
\.


--
-- Data for Name: pipeline_task_logs; Type: TABLE DATA; Schema: public; Owner: emby
--

COPY public.pipeline_task_logs (id, task_id, created_at, level, message) FROM stdin;
1	1	2026-03-19 12:33:02.765428+08	info	任务已创建
2	2	2026-03-19 12:42:25.396797+08	info	任务已创建
3	3	2026-03-19 12:44:02.446273+08	info	任务已创建
4	4	2026-03-19 12:46:52.987035+08	info	任务已创建
5	5	2026-03-19 12:47:58.288325+08	info	任务已创建
6	1	2026-03-19 12:50:12.744571+08	info	开始处理
7	1	2026-03-19 12:50:12.757385+08	info	提取到 1 个链接
8	1	2026-03-19 12:50:12.762653+08	info	未识别到 123/115 链接（已跳过）
9	2	2026-03-19 12:50:12.765628+08	info	开始处理
10	2	2026-03-19 12:50:12.769117+08	info	提取到 1 个链接
11	2	2026-03-19 12:50:12.772248+08	info	未识别到 123/115 链接（已跳过）
12	3	2026-03-19 12:50:12.774934+08	info	开始处理
13	3	2026-03-19 12:50:12.778169+08	info	提取到 1 个链接
14	3	2026-03-19 12:50:12.781287+08	info	未识别到 123/115 链接（已跳过）
15	4	2026-03-19 12:50:12.784027+08	info	开始处理
16	4	2026-03-19 12:50:12.787385+08	info	提取到 1 个链接
17	6	2026-03-19 12:50:12.792899+08	info	任务已创建
18	4	2026-03-19 12:50:12.79689+08	info	已创建 1 个转存任务
19	5	2026-03-19 12:50:12.799723+08	info	开始处理
20	5	2026-03-19 12:50:12.804032+08	info	提取到 1 个链接
21	7	2026-03-19 12:50:12.808042+08	info	任务已创建
22	5	2026-03-19 12:50:12.814686+08	info	已创建 1 个转存任务
23	6	2026-03-19 12:50:22.695662+08	info	开始处理
24	6	2026-03-19 12:50:22.700451+08	info	该任务类型暂未实现执行器（已占位）
25	7	2026-03-19 12:50:22.702876+08	info	开始处理
26	7	2026-03-19 12:50:22.70785+08	info	该任务类型暂未实现执行器（已占位）
27	8	2026-03-19 12:51:49.199019+08	info	任务已创建
28	8	2026-03-19 12:51:52.695677+08	info	开始处理
29	8	2026-03-19 12:51:52.700695+08	info	该任务类型暂未实现执行器（已占位）
\.


--
-- Data for Name: pipeline_tasks; Type: TABLE DATA; Schema: public; Owner: emby
--

COPY public.pipeline_tasks (id, created_at, updated_at, type, status, title, payload_json) FROM stdin;
1	2026-03-19 12:33:02.732152+08	2026-03-19 12:50:12.762643+08	tg_message	success	test tg ingest	{"text": "test tg ingest\\nhttps://example.com", "chat_id": 6260525687, "from_id": 6260525687}
2	2026-03-19 12:42:25.393418+08	2026-03-19 12:50:12.772235+08	tg_message	success	tg bot self-test https://example.com	{"text": "tg bot self-test https://example.com", "chat_id": -1003320851407, "from_id": 6260525687, "message_id": 999999}
3	2026-03-19 12:44:02.443005+08	2026-03-19 12:50:12.781244+08	tg_message	success	https://youtu.be/eXxZkj-Y7es?si=PXZPjJhLoOYw_mDm	{"chat_id": 6260525687, "chat_type": "private", "from_id": 6260525687, "from_name": "Jay Ceng", "message_id": 1183, "text": "https://youtu.be/eXxZkj-Y7es?si=PXZPjJhLoOYw_mDm", "username": ""}
4	2026-03-19 12:46:52.982744+08	2026-03-19 12:50:12.796882+08	tg_message	success	https://www.123912.com/s/O5KATd-mjVWd?notoken=1&pwd=SYGY	{"chat_id": 6260525687, "chat_type": "private", "from_id": 6260525687, "from_name": "Jay Ceng", "message_id": 1185, "text": "https://www.123912.com/s/O5KATd-mjVWd?notoken=1&pwd=SYGY", "username": ""}
5	2026-03-19 12:47:58.280868+08	2026-03-19 12:50:12.814664+08	tg_message	success	📺 电视剧：优雅贵族的休假指南。 (2026) - S01E11	{"chat_id": 6260525687, "chat_type": "private", "from_id": 6260525687, "from_name": "Jay Ceng", "message_id": 1186, "text": "📺 电视剧：优雅贵族的休假指南。 (2026) - S01E11\\n🍿 TMDB ID: 274141\\n⭐️ 评分: 8.9\\n🎭 类型: 动画,动作冒险,Sci-Fi & Fantasy\\n📂 分类: 日漫\\n🎞️ 质量: WEB-DL 1080p\\n📦 文件: 1 个\\n💾 大小: 1.36 GB\\n👥 主演: 斉藤 壮馬,梅原 裕一郎\\n📝 简介: 　　青年利瑟尔在奇幻世界中作为宰相大显身手。一天，他突然穿越到了另一个异世界。不过，他活用了自己与生俱来的头脑与话术，让高级冒险者劫尔成为了伙伴，自己也华丽转型为冒险者。明明有可能回不到原来的世界，却...\\n\\n🔗 链接: https://115cdn.com/s/swfabmg36ty?password=p932\\n\\n#日漫", "username": ""}
6	2026-03-19 12:50:12.78935+08	2026-03-19 12:50:22.700444+08	transfer	success	转存(123)	{"provider": "123", "url": "https://www.123912.com/s/O5KATd-mjVWd?notoken=1&pwd=SYGY", "pwd": "SYGY", "source": {"task_id": 4, "chat_id": 6260525687, "from_id": 6260525687, "message_id": 1185}, "media": {}, "raw_text": "https://www.123912.com/s/O5KATd-mjVWd?notoken=1&pwd=SYGY"}
7	2026-03-19 12:50:12.80689+08	2026-03-19 12:50:22.707843+08	transfer	success	转存(115) 优雅贵族的休假指南。 (2026) - S01E11	{"provider": "115", "url": "https://115cdn.com/s/swfabmg36ty?password=p932", "password": "p932", "source": {"task_id": 5, "chat_id": 6260525687, "from_id": 6260525687, "message_id": 1186}, "media": {"tmdb_id": 274141, "season": 1, "episode": 11, "title": "优雅贵族的休假指南。 (2026) - S01E11", "media_type": "series", "tags": ["日漫"]}, "raw_text": "📺 电视剧：优雅贵族的休假指南。 (2026) - S01E11\\n🍿 TMDB ID: 274141\\n⭐️ 评分: 8.9\\n🎭 类型: 动画,动作冒险,Sci-Fi & Fantasy\\n📂 分类: 日漫\\n🎞️ 质量: WEB-DL 1080p\\n📦 文件: 1 个\\n💾 大小: 1.36 GB\\n👥 主演: 斉藤 壮馬,梅原 裕一郎\\n📝 简介: 　　青年利瑟尔在奇幻世界中作为宰相大显身手。一天，他突然穿越到了另一个异世界。不过，他活用了自己与生俱来的头脑与话术，让高级冒险者劫尔成为了伙伴，自己也华丽转型为冒险者。明明有可能回不到原来的世界，却...\\n\\n🔗 链接: https://115cdn.com/s/swfabmg36ty?password=p932\\n\\n#日漫"}
8	2026-03-19 12:51:49.19624+08	2026-03-19 12:51:52.700683+08	emby_refresh	success	emby_refresh	{}
\.


--
-- Name: library_snapshots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: emby
--

SELECT pg_catalog.setval('public.library_snapshots_id_seq', 1, true);


--
-- Name: pipeline_task_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: emby
--

SELECT pg_catalog.setval('public.pipeline_task_logs_id_seq', 29, true);


--
-- Name: pipeline_tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: emby
--

SELECT pg_catalog.setval('public.pipeline_tasks_id_seq', 8, true);


--
-- Name: kv_settings kv_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: emby
--

ALTER TABLE ONLY public.kv_settings
    ADD CONSTRAINT kv_settings_pkey PRIMARY KEY (key);


--
-- Name: library_snapshots library_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: emby
--

ALTER TABLE ONLY public.library_snapshots
    ADD CONSTRAINT library_snapshots_pkey PRIMARY KEY (id);


--
-- Name: pipeline_task_logs pipeline_task_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: emby
--

ALTER TABLE ONLY public.pipeline_task_logs
    ADD CONSTRAINT pipeline_task_logs_pkey PRIMARY KEY (id);


--
-- Name: pipeline_tasks pipeline_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: emby
--

ALTER TABLE ONLY public.pipeline_tasks
    ADD CONSTRAINT pipeline_tasks_pkey PRIMARY KEY (id);


--
-- Name: library_snapshots uq_library_snapshots_day; Type: CONSTRAINT; Schema: public; Owner: emby
--

ALTER TABLE ONLY public.library_snapshots
    ADD CONSTRAINT uq_library_snapshots_day UNIQUE (day);


--
-- Name: ix_pipeline_task_logs_task_id; Type: INDEX; Schema: public; Owner: emby
--

CREATE INDEX ix_pipeline_task_logs_task_id ON public.pipeline_task_logs USING btree (task_id);


--
-- Name: ix_pipeline_task_logs_task_id_created; Type: INDEX; Schema: public; Owner: emby
--

CREATE INDEX ix_pipeline_task_logs_task_id_created ON public.pipeline_task_logs USING btree (task_id, created_at);


--
-- Name: ix_pipeline_tasks_status_created; Type: INDEX; Schema: public; Owner: emby
--

CREATE INDEX ix_pipeline_tasks_status_created ON public.pipeline_tasks USING btree (status, created_at);


--
-- PostgreSQL database dump complete
--

\unrestrict Ln7gnfExaQfVL8m186Xt3RD5fY9CPXzmFXhcFnX80qFSmiQoTsAcaT4hLmfWeL5

