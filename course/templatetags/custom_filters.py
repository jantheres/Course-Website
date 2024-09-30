import re
from django import template

register = template.Library()

@register.filter
def youtube_id(url):
    # Use a regular expression to extract the video ID from the URL
    match = re.search(r'(?<=watch\?v=|/|)([a-zA-Z0-9_-]{11})', url)
    return match.group(0) if match else None