from django import template

register = template.Library()

@register.filter
def default_image(image, default_path="images/default.png"):
    if image:
        try:
            return image.url
        except ValueError:
            pass
    return f"/static/{default_path}"