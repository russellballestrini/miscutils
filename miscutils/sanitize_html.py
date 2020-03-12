from markdown import markdown

from functools import partial

from collections import defaultdict

from bleach.sanitizer import Cleaner
from bleach.linkifier import LinkifyFilter
from bleach.callbacks import nofollow, target_blank

from bleach_whitelist import markdown_tags, markdown_attrs, all_styles

from bs4 import BeautifulSoup

import miniuri

import logging

log = logging.getLogger(__name__)

default_tag_acl = defaultdict(list)


def default_cleaner(tag_acl=None):
    """
    Returns a default Cleaner object.

    We use BeautifulSoup to conditionally whitelist or blacklist
    tags based on tag attr_name and attr_value pairs.
    
    For example, this will whitelist Mathjax script tags:
    
    tag_acl = {
        "script": [
            ("type", "math/tex; mode=display", "allow"),
        ],
    }

    While this example will blacklist Mathjax script tags:
    
    tag_acl = {
        "script": [
            ("type", "math/tex; mode=display", "deny"),
        ],
    }
    
    """
    if tag_acl is None:
        tag_acl.keys = {}

    maybe_safe_tags = ["pre", "table", "tr", "td"]

    tags = maybe_safe_tags + tag_acl.keys() + markdown_tags
    attrs = markdown_attrs

    attrs["img"].append("width")
    attrs["span"] = ["class"]

    # Whitelist and blacklist tag_name/attr/attr_value to get past bleach.
    # We will conditionally filter tags using BeautifulSoup.
    for tag_name in tag_acl.keys():

        # tag_name, for example "script".

        for attr_name, attr_value, allow_or_deny in tag_acl[tag_name]:

            if allow_or_deny == "allow":

                # attr_name, for example "type".
                # attr_value, for example "math/tex; mode=display".

                if tag_name not in attrs:
                    # if tag_name not in attrs, create it as an empty list.
                    attrs[tag_name] = []

                # append the attr_name to the map of approved
                # attributes for the given tag_name.
                attrs[tag_name].append(attr_name)

    cleaner = Cleaner(tags=tags, attributes=attrs, styles=all_styles)

    # disable link_protection by default.
    cleaner.link_protection = False
    # an None signifies a relative URI, which should always be whitelisted.
    cleaner.whitelist_domains = [None]
    # absolute domain, used for turning relative paths into absolute.
    cleaner.absolute_domain = ""
    # add conditional_whitelist_tags to cleaner object.
    cleaner.tag_acl = tag_acl

    return cleaner


def markdown_to_raw_html(data):
    """Accepts a markdown string, returns raw unsanitized HTML"""
    return markdown(
        data,
        extensions=[
            "markdown.extensions.codehilite",
            "markdown.extensions.fenced_code",
            "mdx_math",
        ],
    )


def conditional_tag_filter(soup, cleaner):
    """
    Use BeautifulSoup `Soup` object to filter out non-whitelisted tags.
    """

    # bleach does not have a way to conditionally accept tags whitelists.
    for tag_name in cleaner.tag_acl.keys():

        # tag_name for example "script"

        for attr_name, attr_value, allow_or_deny in cleaner.tag_acl[tag_name]:

            #
            # tag attr_name:
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
            # allow_or_deny:
            #
            #  * "allow"
            #  * "deny"
            #
            log.info("{} {} {}".format(attr_name, attr_value, allow_or_deny))

            for tag in soup.find_all(tag_name):

                # tag is a BeautifulSoup tag object.
                log.info("{}".format(tag.attrs.get(attr_name)))

                if allow_or_deny == "allow":

                    if tag.attrs.get(attr_name) == attr_value:
                        # this tag attr_name/attr_value is whitelisted.
                        continue

                log.debug(
                    "Extracting {} tag with attr_name {} and attr_value {}".format(
                        tag_name, attr_name, attr_value
                    )
                )
                # remove this tag.
                # this tag attr_name:attr_value is _not_ whitelisted.
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

    return soup


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
