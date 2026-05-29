"""
Daily Learning Lab — Post Generator
Fetches a poem, artwork, history events from free APIs,
picks an essay/story/life-lesson from the curated catalog,
and writes a Jekyll-compatible Markdown post.
"""

import requests
import json
import random
import sys
from datetime import date, datetime
from pathlib import Path

CATALOG_PATH = Path(__file__).parent / "data" / "catalog.json"
POSTS_DIR = Path(__file__).parent / "_posts"
USED_PATH = Path(__file__).parent / "data" / "used.json"


def load_used():
    """Load the set of previously used item IDs to prevent repeats."""
    if USED_PATH.exists():
        return json.loads(USED_PATH.read_text())
    return {"poems": [], "artworks": [], "essays": [], "stories": [], "life_lessons": []}


def save_used(used):
    USED_PATH.write_text(json.dumps(used, indent=2))


def get_poem(used):
    """Random poem from PoetryDB, avoiding repeats."""
    for _ in range(10):  # retry up to 10 times to avoid duplicates
        try:
            resp = requests.get("https://poetrydb.org/random", timeout=15)
            resp.raise_for_status()
            poem = resp.json()[0]
            key = f"{poem['author']}|{poem['title']}"
            if key in used["poems"]:
                continue
            used["poems"].append(key)
            lines = poem["lines"]
            # Show first 16 lines max for readability
            preview = "\n> ".join(lines[:16])
            if len(lines) > 16:
                preview += "\n> ..."
            return {
                "title": poem["title"],
                "author": poem["author"],
                "text": preview,
                "line_count": len(lines),
            }
        except Exception as e:
            print(f"  PoetryDB attempt failed: {e}", file=sys.stderr)
            continue
    # Fallback
    return {
        "title": "Invictus",
        "author": "William Ernest Henley",
        "text": (
            "Out of the night that covers me,\n> Black as the pit from pole to pole,\n> "
            "I thank whatever gods may be\n> For my unconquerable soul."
        ),
        "line_count": 16,
    }


def get_artwork(used):
    """Random artwork from Art Institute of Chicago API."""
    for _ in range(10):
        try:
            page = random.randint(1, 800)
            resp = requests.get(
                "https://api.artic.edu/api/v1/artworks",
                params={
                    "limit": 5,
                    "page": page,
                    "fields": "id,title,artist_display,date_display,image_id,thumbnail,place_of_origin,medium_display",
                },
                timeout=15,
            )
            resp.raise_for_status()
            artworks = [a for a in resp.json()["data"] if a.get("image_id")]
            if not artworks:
                continue
            art = random.choice(artworks)
            key = str(art["id"])
            if key in used["artworks"]:
                continue
            used["artworks"].append(key)
            image_url = f"https://www.artic.edu/iiif/2/{art['image_id']}/full/843,/0/default.jpg"
            return {
                "title": art["title"],
                "artist": art["artist_display"] or "Unknown",
                "date": art["date_display"] or "Unknown date",
                "medium": art.get("medium_display", ""),
                "origin": art.get("place_of_origin", ""),
                "image_url": image_url,
                "link": f"https://www.artic.edu/artworks/{art['id']}",
            }
        except Exception as e:
            print(f"  Art API attempt failed: {e}", file=sys.stderr)
            continue
    # Fallback
    return {
        "title": "The Starry Night",
        "artist": "Vincent van Gogh",
        "date": "1889",
        "medium": "Oil on canvas",
        "origin": "France",
        "image_url": "https://www.artic.edu/iiif/2/e966799b-97ee-1cc6-bd2f-a94b4b8bb8f9/full/843,/0/default.jpg",
        "link": "https://www.artic.edu/artworks/28560",
    }


def get_history():
    """On this day events from Wikipedia API."""
    today = date.today()
    try:
        resp = requests.get(
            f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/events/{today.month}/{today.day}",
            headers={"User-Agent": "DailyLearningLab/1.0"},
            timeout=15,
        )
        resp.raise_for_status()
        events = resp.json().get("events", [])
        # Pick 3 diverse events from different centuries if possible
        if len(events) > 3:
            selected = random.sample(events, 3)
        else:
            selected = events
        return [{"year": e["year"], "text": e["text"]} for e in selected]
    except Exception as e:
        print(f"  Wikipedia API failed: {e}", file=sys.stderr)
        return [{"year": 1953, "text": "Edmund Hillary and Tenzing Norgay reached the summit of Mount Everest."}]


def pick_from_catalog(category, used):
    """Pick an unused item from a catalog category."""
    catalog = json.loads(CATALOG_PATH.read_text())
    items = catalog.get(category, [])
    unused = [i for i in items if i.get("id") not in used.get(category, [])]
    if not unused:
        # Reset if all used
        used[category] = []
        unused = items
    if not unused:
        return None
    item = random.choice(unused)
    used[category].append(item["id"])
    return item


def format_post(poem, artwork, essay, story, lesson, history):
    """Format everything into a Jekyll Markdown post."""
    today = date.today()
    title_date = today.strftime("%d %B %Y")
    file_date = today.strftime("%Y-%m-%d")

    post = f"""---
layout: post
title: "Daily Learning Lab — {title_date}"
date: {file_date}
categories: learning
---

## 📜 Poem of the Day

**"{poem['title']}"** — *{poem['author']}*

> {poem['text']}

---

## 🎨 Art Masterpiece

![{artwork['title']}]({artwork['image_url']})

**{artwork['title']}** — {artwork['artist']} ({artwork['date']})"""

    if artwork.get("medium"):
        post += f"\n\n*{artwork['medium']}*"

    post += f"\n\n[View full details →]({artwork['link']})"

    post += "\n\n---\n\n## 📝 Short Essay\n\n"
    if essay:
        post += f"**{essay['title']}** — {essay['author']}\n\n"
        post += f"*{essay['hook']}*\n\n"
        post += f"🔗 [Read here]({essay['link']})\n\n"
        if essay.get("topic"):
            post += f"Topic: {essay['topic']}\n"
    else:
        post += "*No essay available — add more to your catalog!*\n"

    post += "\n---\n\n## 📖 Short Story\n\n"
    if story:
        post += f"**{story['title']}** — {story['author']}"
        if story.get("reading_time"):
            post += f" (~{story['reading_time']})"
        post += "\n\n"
        if story.get("genre"):
            post += f"*Genre: {story['genre']}*\n\n"
        post += f"🔗 [Read here]({story['link']})\n"
    else:
        post += "*No story available — add more to your catalog!*\n"

    post += "\n---\n\n## 💡 Life Lesson\n\n"
    if lesson:
        post += f"> {lesson['maxim']}\n"
        if lesson.get("source"):
            post += f">\n> — *{lesson['source']}*\n"
        post += f"\n**Reflection:** {lesson['reflection']}\n"
    else:
        post += "*No lesson available — add more to your catalog!*\n"

    post += "\n---\n\n## 📅 On This Day in History\n\n"
    for event in history:
        post += f"- **{event['year']}** — {event['text']}\n"

    post += "\n---\n\n*Generated automatically by the [Daily Learning Lab](https://github.com/Seosamh19/daily-learning-lab)*\n"

    return post, file_date


def main():
    print("🧠 Generating Daily Learning Lab post...")

    used = load_used()

    print("  Fetching poem...")
    poem = get_poem(used)
    print(f"    ✓ {poem['title']} by {poem['author']}")

    print("  Fetching artwork...")
    artwork = get_artwork(used)
    print(f"    ✓ {artwork['title']} by {artwork['artist']}")

    print("  Fetching history...")
    history = get_history()
    print(f"    ✓ {len(history)} events")

    print("  Picking essay from catalog...")
    essay = pick_from_catalog("essays", used)
    if essay:
        print(f"    ✓ {essay['title']}")

    print("  Picking story from catalog...")
    story = pick_from_catalog("stories", used)
    if story:
        print(f"    ✓ {story['title']}")

    print("  Picking life lesson...")
    lesson = pick_from_catalog("life_lessons", used)
    if lesson:
        print(f"    ✓ {lesson.get('source', 'Original')}")

    print("  Formatting post...")
    post_content, file_date = format_post(poem, artwork, essay, story, lesson, history)

    # Write the post
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    post_path = POSTS_DIR / f"{file_date}-daily-learning-lab.md"
    post_path.write_text(post_content)
    print(f"  ✓ Post written to {post_path}")

    # Save used items
    save_used(used)
    print("  ✓ Usage tracking updated")
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
