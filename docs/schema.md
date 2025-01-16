# Database Schema

## companies

```sql
CREATE TABLE companies (
    id text PRIMARY KEY,
    name text,
    domain text,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    logo_url text,
    description text,
    external_description text,
    country text,
    tags jsonb,
    type text,
    headcount numeric,
    funding_total numeric,
    funding_stage text,
    funding_at timestamp with time zone,
    founded_at timestamp with time zone,
    topic_id bigint REFERENCES topics(id),
    topic_probability numeric,
    geography character varying
);
```

## github_organizations

```sql
CREATE TABLE github_organizations (
    id text PRIMARY KEY,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    name text,
    url text,
    homepage_url text,
    followers numeric,
    company_id text REFERENCES companies(id) ON DELETE CASCADE ON UPDATE CASCADE
);
```

## github_repositories

```sql
CREATE TABLE github_repositories (
    id text PRIMARY KEY,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    full_name text,
    name text,
    url text,
    description text,
    readme text,
    fork boolean,
    pushed_at timestamp with time zone,
    homepage_url text,
    size numeric,
    stargazers_count numeric,
    watchers_count numeric,
    forks_count numeric,
    language text,
    archived boolean,
    disabled boolean,
    license_key text,
    license_name text,
    license_url text,
    topics jsonb,
    organization_id text REFERENCES github_organizations(id) ON DELETE CASCADE ON UPDATE CASCADE
);
```

## harmonic_data

```sql
CREATE TABLE harmonic_data (
    company_id text REFERENCES companies(id) ON DELETE CASCADE ON UPDATE CASCADE,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    value numeric,
    type text,
    source text,
    date timestamp with time zone,
    CONSTRAINT harmonic_data_pkey PRIMARY KEY (company_id, type, source, date)
);
```

## pdl_headcount_sales_eng

```sql
CREATE TABLE pdl_headcount_sales_eng (
    id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name text NOT NULL,
    other_uncategorized bigint,
    trades bigint,
    operations bigint,
    customer_service bigint,
    legal bigint,
    public_relations bigint,
    real_estate bigint,
    design bigint,
    education bigint,
    media bigint,
    marketing bigint,
    human_resources bigint,
    sales bigint,
    health bigint,
    finance bigint,
    engineering bigint
);
```

## peopledatabase

```sql
CREATE TABLE peopledatabase (
    name text,
    employee_count_by_role json,
    average_employee_tenure json,
    employee_churn_rate json,
    employee_growth_rate json,
    last_funding_date json,
    latest_funding_stage json,
    id text PRIMARY KEY,
    founded bigint,
    country text,
    industry text,
    number_founding_rounds bigint,
    total_funding_raised double precision,
    linkedin_followers text,
    tags json
);
```

## peopledatabase_enriched

```sql
CREATE TABLE peopledatabase_enriched (
    name text,
    employee_count_by_role json,
    average_employee_tenure json,
    employee_churn_rate json,
    employee_growth_rate json,
    last_funding_date json,
    latest_funding_stage json,
    id text PRIMARY KEY,
    founded bigint,
    country json,
    industry text,
    number_funding_rounds bigint,
    total_funding_raised double precision,
    linkedin_follower_count text,
    tags json
);
```

## predict_leads_news

```sql
CREATE TABLE predict_leads_news (
    id uuid PRIMARY KEY,
    company_id text NOT NULL REFERENCES companies(id) ON DELETE CASCADE ON UPDATE CASCADE,
    summary text,
    category text,
    found_at timestamp with time zone,
    confidence numeric,
    article_sentence text,
    human_approved boolean,
    planning boolean,
    article_id text,
    article_author text,
    article_body text,
    article_image_url text,
    article_url text,
    article_published_at timestamp with time zone,
    article_title text,
    amount text,
    amount_normalized numeric,
    product text,
    product_data jsonb,
    effective_date date,
    event text,
    financing_type text,
    financing_type_normalized text,
    headcount bigint,
    job_title text,
    recognition text,
    vulnerability text,
    asset_tags text[],
    financing_type_tags text[],
    job_title_tags text[],
    product_tags text[],
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
```

## similarweb_data

```sql
CREATE TABLE similarweb_data (
    company_id text REFERENCES companies(id),
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    domain text,
    category text,
    global_rank numeric,
    category_rank numeric,
    country_rank numeric,
    similar_sites text,
    estimated_monthly_visits jsonb[],
    engagments jsonb,
    CONSTRAINT similarweb_data_pkey PRIMARY KEY (company_id, domain)
);
```

## similarweb_data_timeperiod

```sql
CREATE TABLE similarweb_data_timeperiod (
    company_id text,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    type text,
    visit_date timestamp without time zone,
    visit_count numeric,
    domain text,
    CONSTRAINT similarweb_data_timeperiod_pkey PRIMARY KEY (company_id, type, visit_date, domain)
);
```

## submarkets

```sql
CREATE MATERIALIZED VIEW submarkets AS  SELECT t.id,
    t.topic_name,
    t.topic_description,
    min(c.founded_at) AS earliest_founded_at,
    count(c.id) AS company_count,
    sum(c.funding_total) AS total_funding,
    jsonb_agg(DISTINCT c.funding_stage) AS funding_stages,
    ( SELECT c2.geography
           FROM companies c2
          WHERE c2.topic_id = t.id
          GROUP BY c2.geography
          ORDER BY (count(c2.geography)) DESC, c2.geography
         LIMIT 1) AS most_common_geography
   FROM topics t
     LEFT JOIN companies c ON c.topic_id = t.id
  GROUP BY t.id;
```

## submarkets_companies

```sql
CREATE MATERIALIZED VIEW submarkets_companies AS  WITH ranked_companies AS (
         SELECT c.id,
            c.name,
            c.domain,
            c.created_at,
            c.updated_at,
            c.logo_url,
            c.description,
            c.external_description,
            c.country,
            c.tags,
            c.type,
            c.headcount,
            c.funding_total,
            c.funding_stage,
            c.funding_at,
            c.founded_at,
            c.topic_id,
            c.topic_probability,
            c.geography,
            row_number() OVER (PARTITION BY c.topic_id ORDER BY c.topic_probability DESC) AS rank
           FROM companies c
        )
 SELECT ranked_companies.id,
    ranked_companies.name,
    ranked_companies.domain,
    ranked_companies.created_at,
    ranked_companies.updated_at,
    ranked_companies.logo_url,
    ranked_companies.description,
    ranked_companies.external_description,
    ranked_companies.country,
    ranked_companies.tags,
    ranked_companies.type,
    ranked_companies.headcount,
    ranked_companies.funding_total,
    ranked_companies.funding_stage,
    ranked_companies.funding_at,
    ranked_companies.founded_at,
    ranked_companies.topic_id,
    ranked_companies.topic_probability,
    ranked_companies.geography,
    ranked_companies.rank
   FROM ranked_companies
  WHERE ranked_companies.rank <= 4;
```

## topics

```sql
CREATE TABLE topics (
    id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    topic_name text,
    topic_description text
);
```