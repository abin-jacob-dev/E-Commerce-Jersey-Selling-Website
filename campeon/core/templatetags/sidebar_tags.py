from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_class(context, *view_names):
    current = context["request"].resolver_match.view_name

    base = "flex items-center gap-4 text-xs font-bold uppercase tracking-widest"

    if current in view_names:
        return (
            f"{base} text-black bg-lime-100 rounded-lg px-3 py-2"
        )

    return f"{base} text-black-400 hover:text-black"