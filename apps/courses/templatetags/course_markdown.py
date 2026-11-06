
from html import escape

from django import template
from django.utils.safestring import mark_safe

from markdown_it import MarkdownIt

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound


register = template.Library()

# Configure Markdown parser.
markdown_parser = MarkdownIt(
    "commonmark",
    {
        "html": False,
        "linkify": False,
        "breaks": True,
    },
)

markdown_parser.enable("table")
markdown_parser.disable("image")

# Configure syntax highlighting.
code_formatter = HtmlFormatter(
    style="monokai",
    nowrap=True,
    noclasses=True,
)


def render_code(renderer, tokens, idx, options, env):
    token = tokens[idx]

    language = (
        token.info.strip().split()[0]
        if token.info.strip()
        else "text"
    )

    try:
        lexer = get_lexer_by_name(language)
    except ClassNotFound:
        lexer = TextLexer()

    highlighted_code = highlight(
        token.content,
        lexer,
        code_formatter,
    )

    return (
        '<div class="lesson-code-block">'
        f'<span class="lesson-code-language">'
        f'{escape(language)}</span>'
        f'<pre><code>{highlighted_code}</code></pre>'
        '</div>'
    )


markdown_parser.add_render_rule(
    "fence",
    render_code,
)


@register.filter(name="render_markdown")
def render_markdown(value):
    html = markdown_parser.render(value or "")
    return mark_safe(html)
