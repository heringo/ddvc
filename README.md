# DDV Market Trend

![alt text](https://i.imgur.com/O8vZHPM.png)

> This project was built as part of the Data-Driven VC Hackathon organized by [Red River West](https://redriverwest.com) & [Bivwak! by BNP Paribas](https://bivwak.bnpparibas/)

## Prerequisites

### Rye

```bash
brew install rye
```

```bash
rye sync
```

### Supabase

We're using [Supabase](https://supabase.com) as our database, you'll need to create a project and get the database URL.

## Table Schema

See [docs/schema.md](docs/schema.md)

## Code Structure

- [src/collect](src/collect): Data collection scripts
- [src/nlp_pipeline](src/nlp_pipeline): NLP pipeline scripts
- [src/utils](src/utils): Utility scripts (e.g. database connection)
- [front](front): Frontend code

## Data collection

Add a `.env` file in the root of the project based on `.env.example`

Run the following commands to collect data:

```bash
rye run harmonic
rye run predictleads
rye run predictleads_news
rye run pdl_headcount_sales_eng
```

## NLP pipeline

See [docs/nlp_pipeline.md](docs/nlp_pipeline.md)

## Next Steps for a Comprehensive Product

### Features
- Expand the dataset by including more companies and enhancing clustering with additional media sources (e.g., news articles, website content, etc.).
- Introduce user-created taxonomies for a personalized and tailored experience.
- Enrich cluster information with more data to deterministically identify whether a segment is trending.

### Technical Enhancements
- Implement embedding pipelines in **Airflow** for optimized orchestration and scalability.
- Deploy the application online for broader accessibility.
- Improve database latency by hosting the database for faster and more reliable performance.
