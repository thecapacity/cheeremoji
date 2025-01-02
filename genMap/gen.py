import emoji
import json

## https://pypi.org/project/emoji/

### Examples:
"""
print(emoji.emojize('Python is :thumbs_up:'))
print(emoji.emojize('Python is :thumbsup:', language='alias'))
print(emoji.demojize('Python is 👍'))
print(emoji.emojize("Python is fun :red_heart:"))
print(emoji.emojize("Python is fun :red_heart:", variant="emoji_type"))
print(emoji.is_emoji("👍"))
"""

emoji_map = {
    v['en'] : k for k, v in emoji.EMOJI_DATA.items()
    if v.get('en', None)
}

with open("emojiMap.json", "w", encoding="utf-8") as f:
    json.dump(emoji_map, f, ensure_ascii=False, indent=4)

print("Emoji map saved to emojiMap.json!")
