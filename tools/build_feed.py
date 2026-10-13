"""Rebuild feed.xml from episodes/*.mp3 and their episodes/*.json metadata.

Each episode: episodes/YYYY-MM-DD.mp3 plus episodes/YYYY-MM-DD.json {"title","description"}.
"""
import json, os, glob, subprocess, datetime, html
BASE = "https://kitsunayx1.github.io/daily-audio"
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
items = []
for mp3 in sorted(glob.glob(os.path.join(root, "episodes", "*.mp3")), reverse=True):
    day = os.path.basename(mp3)[:-4]
    meta = json.load(open(mp3[:-4] + ".json"))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3],
                               capture_output=True, text=True).stdout.strip() or 0)
    pub = datetime.datetime.strptime(day, "%Y-%m-%d").replace(hour=10, tzinfo=datetime.timezone.utc)
    items.append(f"""    <item>
      <title>{html.escape(meta['title'])}</title>
      <description>{html.escape(meta.get('description', ''))}</description>
      <link>{BASE}/briefs/{day}.md</link>
      <guid isPermaLink="false">morning-signal-{day}</guid>
      <pubDate>{pub.strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
      <enclosure url="{BASE}/episodes/{day}.mp3" length="{os.path.getsize(mp3)}" type="audio/mpeg"/>
      <itunes:duration>{int(dur)}</itunes:duration>
    </item>""")
feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>Morning Signal</title>
    <link>{BASE}/</link>
    <description>Daily threat intelligence briefing from public sources.</description>
    <language>en-us</language>
    <itunes:author>Morning Signal</itunes:author>
    <itunes:image href="{BASE}/cover.png"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""
open(os.path.join(root, "feed.xml"), "w").write(feed)
print(f"feed.xml: {len(items)} episodes")
