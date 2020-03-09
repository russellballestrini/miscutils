from markdown import markdown

from functools import partial

from bleach.sanitizer import Cleaner
from bleach.linkifier import LinkifyFilter
from bleach.callbacks import nofollow, target_blank

from bleach_whitelist import markdown_tags, markdown_attrs, all_styles

from bs4 import BeautifulSoup

import miniuri


def default_cleaner(conditional_tag_whitelist=None):
    """
    Returns a default Cleaner object.

    We use BeautifulSoup to conditionally whitelist tags 
    based on approved attributes and attribute_value pairs.
    
    For example, this will whitelist Mathjax:
    
    conditional_tag_whitelist = {
        "script": [
            ("type", "math/tex; mode=display"),
        ],
    }
    
    """
    if conditional_tag_whitelist is None:
        conditional_tag_whitelist.keys = {}

    maybe_safe_tags = ["pre", "table", "tr", "td"]

    tags = maybe_safe_tags + conditional_tag_whitelist.keys() + markdown_tags
    attrs = markdown_attrs

    attrs["img"].append("width")
    attrs["span"] = ["class"]

    cleaner = Cleaner(tags=tags, attributes=attrs, styles=all_styles)

    # disable link_protection by default.
    cleaner.link_protection = False
    # an None signifies a relative URI, which should always be whitelisted.
    cleaner.whitelist_domains = [None]
    # absolute domain, used for turning relative paths into absolute.
    cleaner.absolute_domain = ""
    # add conditional_whitelist_tags to cleaner object.
    cleaner.conditional_tag_whitelist = conditional_tag_whitelist
    
    return cleaner


def markdown_to_raw_html(data):
    """Accepts a markdown string, returns raw unsanitized HTML"""
    return markdown(
        data,
        extensions=[
            "markdown.extensions.codehilite",
            "markdown.extensions.fenced_code",
        ],
    )


def conditional_tag_filter(soup, cleaner):
    """
    Use BeautifulSoup `Soup` object to filter out non-whitelisted tags.
    """
     
    # bleach does not have a way to conditionally accept tags whitelists.
    for tag_name in cleaner.conditional_tag_whitelist.keys():

        # tag_name for example "script"

        for tag in soup.find_all(tag_name):

            # tag is a BeautifulSoup tag object.

            for attr, attr_value in cleaner.conditional_tag_whitelist[tag_name]:

                # tag attr:
                #
                #   * "type"
                #   * "id"
                #   * "class"
                #   * ect
                #
                # tag attr_value:
                #
                #   * "math/tex; mode=display"
                #   * "<uuid>"
                #   * ect
                #

                if tag.attrs.get(attr) == attr_value:
                    # this tag attr/attr_value is whitelisted.
                    continue

                # remove this tag.
                # this tag attr:attr_value is not whitelisted.
                tag.extract()

    return soup


def protect_links(soup, cleaner):

    for a_tag in soup.find_all("a"):
        uri = miniuri.Uri(a_tag.attrs.get("href", ""))

        if uri.hostname in cleaner.whitelist_domains:
            # domain in whitelist or relative URI so remove rel="nofollow".
            a_tag.attrs.pop("rel", None)
            if uri.hostname is None and cleaner.absolute_domain:
                # make relative path absolute!
                # TODO: if we hold scheme in Namespace object we can use it
                # when building absolute uris. for now assume https.
                uri.scheme = "https"
                uri.hostname = cleaner.absolute_domain
                a_tag.attrs["href"] = str(uri)

        elif cleaner.link_protection:
            # domain not in whitelist, replace a_tag with "[link removed]".
            a_tag.replace_with("[link removed]")



def clean_raw_html(raw_html, cleaner=None):
    """
    Accepts raw HTML and a cleaner object
    Returns sanitized HTML as bytes.
    """
    if cleaner is None:
        cleaner = default_cleaner()

    if cleaner.link_protection == False:
        cleaner.filters.append(
            partial(
                LinkifyFilter,
                callbacks=[nofollow, target_blank],
                skip_tags=["pre", "code"],
            )
        )

    cleaned_html = cleaner.clean(raw_html)

    soup = BeautifulSoup(cleaned_html, "html5lib")

    # conditionally accept whitelisted tags, filter out the rest.
    soup = conditional_tag_filter(soup, cleaner)

    # protect links from abuse.
    soup = protect_links(soup, cleaner)

    return soup.decode(eventual_encoding="utf-8")
