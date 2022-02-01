import re


def remove_tags(caption: str) -> str:
    pattern = r'<.?span.*?>'
    result = re.sub(pattern, '', caption)
    return result
