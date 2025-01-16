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
