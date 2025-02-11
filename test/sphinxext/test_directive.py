"""
Pytest-ing sphinx directives is `yet undocumented
<https://github.com/sphinx-doc/sphinx/issues/7008>`_
and as explained also in `this sourceforge <>`_ thread,
you may learn more from the `test-cases in the *sphinx* sources
<https://github.com/sphinx-doc/sphinx/blob/master/tests/test_ext_doctest.py>`_
or `similar projects
<https://github.com/pauleveritt/customizing_sphinx/blob/master/tests/integration/test_directive.py>`_.
"""
import os.path as osp
import re
import xml.etree
from typing import Dict
from xml.etree.ElementTree import Element

import html5lib
import pytest

from graphtik.sphinxext import _image_formats

from ..helpers import attr_check, check_xpath, flat_dict

etree_cache: Dict[str, Element] = {}


@pytest.fixture(scope="module")
def cached_etree_parse() -> xml.etree:
    ## Adapted from sphinx testing
    def parse(fpath):
        cache_key = (fpath, fpath.stat().st_mtime)
        if cache_key in etree_cache:
            return etree_cache[fpath]
        try:
            with (fpath).open("rb") as fp:
                etree: xml.etree = html5lib.HTMLParser(
                    namespaceHTMLElements=False
                ).parse(fp)

            # etree_cache.clear() # WHY?
            etree_cache[cache_key] = etree
            return etree
        except Exception as ex:
            raise Exception(f"Parsing document {fpath} failed due to: {ex}") from ex

    yield parse
    etree_cache.clear()


@pytest.fixture(params=_image_formats)
def img_format(request):
    return request.param


@pytest.mark.sphinx(buildername="html", testroot="graphtik-directive")
@pytest.mark.test_params(shared_result="test_count_image_files")
def test_html(make_app, app_params, img_format, cached_etree_parse):
    fname = "index.html"
    args, kwargs = app_params
    app = make_app(
        *args,
        confoverrides={"graphtik_default_graph_format": img_format},
        freshenv=True,
        **kwargs,
    )
    fname = app.outdir / fname
    print(fname)

    ## Clean outdir from previous build to enact re-build.
    #
    try:
        app.outdir.rmtree(ignore_errors=True)
    except Exception:
        pass  # the 1st time should fail.
    finally:
        app.outdir.makedirs(exist_ok=True)

    app.build(True)

    image_dir = app.outdir / "_images"

    if img_format is None:
        img_format = "svg"

    image_files = image_dir.listdir()
    nimages = 9
    if img_format == "png":
        # x2 files for image-maps file.
        tag = "img"
        uri_attr = "src"
    else:
        tag = "object"
        uri_attr = "data"

    assert all(f.endswith(img_format) for f in image_files)
    assert len(image_files) == nimages - 3  # -1 skipIf=true, -1 same name, ???

    etree = cached_etree_parse(fname)
    check_xpath(
        etree,
        fname,
        f".//{tag}",
        attr_check(
            "alt",
            "pipeline1",
            r"'aa': \[1, 2\]",
            "pipeline3",
            "pipeline4",
            "pipeline1",
            "pipelineB",
            count=True,
        ),
    )
    check_xpath(
        etree,
        fname,
        f".//{tag}",
        attr_check(
            uri_attr,
        ),
    )
    check_xpath(etree, fname, ".//*[@class='caption-text']", "Solved ")


def _count_nodes(count):
    def checker(nodes):
        assert len(nodes) == count

    return checker


@pytest.mark.sphinx(buildername="html", testroot="graphtik-directive")
@pytest.mark.test_params(shared_result="default_format")
def test_zoomable_svg(app, cached_etree_parse):
    app.build()
    fname = "index.html"
    print(app.outdir / fname)

    nimages = 9
    etree = cached_etree_parse(app.outdir / fname)
    check_xpath(
        etree,
        fname,
        f".//object[@class='graphtik-zoomable-svg']",
        _count_nodes(nimages - 3),  # -zoomable-options(BUG), -skipIf=true, -same-name
    )
    check_xpath(
        etree,
        fname,
        f".//object[@data-graphtik-svg-zoom-options]",
        _count_nodes(nimages - 3),  # see above
    )
