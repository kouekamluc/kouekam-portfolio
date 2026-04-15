"""
Project-level views for cross-app infrastructure endpoints.
"""
from xml.etree.ElementTree import Element, SubElement, tostring

from django.http import HttpResponse

from .sitemaps import StaticViewSitemap, ProjectSitemap, BlogPostSitemap, TutorialSitemap


SITEMAP_SECTIONS = {
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
    "blog": BlogPostSitemap,
    "tutorials": TutorialSitemap,
}


def _absolute_url(request, path):
    """Build an absolute HTTPS URL for sitemap entries."""
    return request.build_absolute_uri(path)


def _lastmod_value(value):
    """Normalize lastmod values to sitemap-friendly strings."""
    if value is None:
        return None
    if hasattr(value, "date"):
        return value.date().isoformat()
    return str(value)


def sitemap_xml(request):
    """Render a resilient sitemap without depending on Sites table lookups."""
    urlset = Element(
        "urlset",
        {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"},
    )

    for sitemap_cls in SITEMAP_SECTIONS.values():
        sitemap = sitemap_cls()
        for item in sitemap.items():
            try:
                location = sitemap.location(item)
            except Exception:
                continue

            url = SubElement(urlset, "url")
            SubElement(url, "loc").text = _absolute_url(request, location)

            lastmod = getattr(sitemap, "lastmod", None)
            if callable(lastmod):
                normalized_lastmod = _lastmod_value(lastmod(item))
                if normalized_lastmod:
                    SubElement(url, "lastmod").text = normalized_lastmod

            if getattr(sitemap, "changefreq", None):
                SubElement(url, "changefreq").text = sitemap.changefreq

            if getattr(sitemap, "priority", None) is not None:
                SubElement(url, "priority").text = f"{sitemap.priority:.1f}"

    xml_bytes = tostring(urlset, encoding="utf-8", xml_declaration=True)
    return HttpResponse(xml_bytes, content_type="application/xml")
