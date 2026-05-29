# Daily Learning Lab

A 1000-day journey through poetry, art, essays, stories, life lessons, and history — delivered fresh every morning as a blog post.

## What It Does

Every day at 08:47 IST, a GitHub Action automatically generates a new post containing:

| Stream | Source |
|--------|--------|
| **Poem of the Day** | Random from [PoetryDB](https://poetrydb.org) (35,000+ public-domain poems) |
| **Art Masterpiece** | Random from [Art Institute of Chicago API](https://api.artic.edu/docs/) (500,000+ works) |
| **Short Essay** | Curated catalog of free online essays |
| **Short Story** | Curated catalog of public-domain & free stories |
| **Life Lesson** | Wisdom maxims with reflection questions |
| **On This Day** | Historical events from [Wikipedia's On This Day API](https://api.wikimedia.org/) |

Posts are published to GitHub Pages at **[seosamh19.github.io/daily-learning-lab](https://seosamh19.github.io/daily-learning-lab/)**

## No Repeats

The system tracks everything that's been shown in `data/used.json`. Poems, artworks, essays, stories, and life lessons won't repeat until the catalog cycles through completely.

## Project Structure

```
daily-learning-lab/
├── _posts/                  # Generated blog posts (Jekyll)
├── _config.yml              # Jekyll site configuration
├── index.md                 # Blog homepage
├── Gemfile                  # Jekyll dependencies
├── generate_post.py         # The generator script
├── data/
│   ├── catalog.json         # Curated essays, stories & life lessons
│   └── used.json            # Tracks what's been shown (no repeats)
└── .github/
    └── workflows/
        └── learning-lab.yml # Daily cron trigger
```

## Running Locally

```bash
# Install dependency
pip install requests

# Generate today's post
python generate_post.py
```

The post lands in `_posts/YYYY-MM-DD-daily-learning-lab.md`.

## Growing the Catalog

To keep variety high across 1000 days, add entries to `data/catalog.json`:

- **Essays**: Title, author, one-line hook, link, topic
- **Stories**: Title, author, reading time, genre, link
- **Life Lessons**: Maxim, source, reflection question

Each entry needs a unique `id` field (e.g. `essay-026`, `story-026`, `lesson-026`).

## Schedule

The GitHub Action runs daily via cron. To change the time, edit the cron expression in `.github/workflows/learning-lab.yml`.

You can also trigger it manually from the **Actions** tab → **Daily Learning Lab** → **Run workflow**.

## Built With

- Python 3.11
- GitHub Actions (automation)
- GitHub Pages + Jekyll (hosting)
- Free APIs: PoetryDB, Art Institute of Chicago, Wikipedia
