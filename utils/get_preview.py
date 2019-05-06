from urllib.request import urlopen
from urllib.parse import urlparse
from html.parser import HTMLParser
from io import StringIO
from contextlib import contextmanager
from functools import lru_cache

NO_PREVIEW = "https://flowers.next.co.uk/assets/images/md/no-image.png"
class MetaParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta = {}
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("property", "").startswith("og:"):
            self._meta[attrs["property"].strip("og:")] = attrs.get("content")
    
class SimpleHTMLConstructor:
    def __init__(self):
        self._buffer = StringIO()
        self._indent = 0
        
    def nl(self):
        self._buffer.write("\n")
        self._buffer.write(" " * 4 * self._indent)
    
    def write(self, *text):
        self._buffer.write(''.join(text))
        self.nl()
        
    def ctx(self, *args, **kwds):
        with self.tag(*args, **kwds):
            pass
            
    @contextmanager
    def tag(self, tag, close=True, **attrs):
        attrs = self._strip_attrs(attrs)
        try:
            self._buffer.write(f"<{tag}")
            for attr, value in attrs.items():
                self._buffer.write(f" {attr}='{value}'")
            self._buffer.write(">")
            self._indent += 1
            self.nl()
            yield
        finally:
            self._indent -= 1
            self.nl()
            if close:
                self._buffer.write(f"</{tag}>")
            
            
    @staticmethod
    def _strip_attrs(attrs):
        if 'cls' in attrs:
            attrs['class'] = attrs.pop('cls')
        return attrs
    
    def __str__(self):
        return self._buffer.getvalue()
    

class InsufficientTags(Exception):
    pass
    
def obtain_image(base, image):
    if image.startswith('/'):
        image = f"{url.scheme}://{url.netloc}{image}"
    return image

def construct_preview(url, meta):
    _url = urlparse(url)
    if not all(map(lambda tag: tag in meta, {"title"})):
        title = url.netloc
        
    html = SimpleHTMLConstructor()
    with html.tag("div", cls="row"):
        with html.tag("div", cls="col-3"):
            with html.tag("a", href=url):
                html.ctx("img", close=False, src=obtain_image(_url, meta.get("image", NO_PREVIEW)), alt=meta.get("title"), cls="img-thumbnail")
        with html.tag("div", cls="col-9"):
            with html.tag("h3"):
                html.write(meta["title"])
                html.ctx("br", close=False)
            if meta.get("description"):
                with html.tag("p"):
                    html.write(meta["description"])

    return str(html)

@lru_cache(None)
def _get_preview(url):
    parser = MetaParser()
    with urlopen(url) as conn:
        headers = conn.info()
        parser.feed(conn.read().decode())

    return construct_preview(url, parser._meta)
