from django import template

register = template.Library()


@register.filter(name='slice_words')
def slice_words(value, arg):
    """
    Custom template filter to slice a string into words and return the first 'n' words.
    """
    words = value.split()
    try:
        count = int(arg)
    except ValueError:
        return value
    result = ' '.join(words[:count])
    if len(words) > count:
        result += '...'
    return result
