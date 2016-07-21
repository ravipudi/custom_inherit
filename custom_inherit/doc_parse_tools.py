from __future__ import absolute_import
from collections import OrderedDict
import inspect

__all__ = ["merge_numpy_docs"]


def parse_numpy_doc(doc):
    """ Extract the text from the various sections of a numpy-formatted docstring.

        Parameters
        ----------
        doc: Union[str, None]

        Returns
        -------
        OrderedDict[str, Union[None,str]]
            The extracted numpy-styled docstring sections."""

    doc_sections = OrderedDict([("Short Summary", None),
                                ("Deprecation Warning", None),
                                ("Parameters", None),
                                ("Attributes", None),
                                ("Extended Summary", None),
                                ("Parameters", None),
                                ("Returns", None),
                                ("Yields", None),
                                ("Other Parameters", None),
                                ("Raises", None),
                                ("See Also", None),
                                ("Notes", None),
                                ("References", None),
                                ("Examples", None)])

    if not doc:
        return doc_sections

    doc = inspect.cleandoc(doc)
    lines = iter(doc.splitlines())

    key = "Short Summary"
    body = []
    while True:
        try:
            line = next(lines)
            if line in doc_sections:
                doc_sections[key] = "\n".join(body).rstrip() if body else None
                body = []
                key = line
                next(lines)  # skip section delimiter
            else:
                body.append(line)
        except StopIteration:
            doc_sections[key] = "\n".join(body)
            break

    return doc_sections


def merge_section(key, prnt_sec, child_sec):
    """ Synthesize a output numpy docstring section.

        Parameters
        ----------
        key: str
            The numpy-section being merged.
        prnt_sec: Union[str, None]
            The docstring section from the parent's attribute.
        child_sec: Union[str, None]
            The docstring section from the child's attribute.
        Returns
        -------
        str
            The output docstring section."""
    if prnt_sec is None and child_sec is None:
        return None

    if key == "Short Summary":
        header = ''
    else:
        header = "\n".join((key, "-".join("" for i in range(len(key))), ""))

    if child_sec is None:
        body = prnt_sec
    else:
        body = child_sec

    return header + body


def merge_all_sections(prnt_sctns, child_sctns):
    """ Merge the doc-sections of the parent's and child's attribute into a single docstring.

        Parameters
        ----------
        prnt_sctns: OrderedDict[str, Union[None,str]]
        child_sctns: OrderedDict[str, Union[None,str]]

        Returns
        -------
        str
            Output docstring of the merged docstrings."""
    doc = []
    if prnt_sctns["Raises"] and (child_sctns["Returns"] or child_sctns["Yields"]):
        prnt_sctns["Raises"] = None

    for key in prnt_sctns:
        sect = merge_section(key, prnt_sctns[key], child_sctns[key])
        if sect is not None:
            doc.append(sect)
    return "\n\n".join(doc) if doc else None


def merge_numpy_docs(prnt_doc, child_doc):
    """ Merge two numpy-style docstrings into a single docstring.

        Given the numpy-style docstrings from a parent and child's attributes, merge the docstring
        sections such that the child's section is used, wherever present, otherwise the parent's
        section is used.

        Parameters
        ----------
        prnt_doc: Union[None, str]
            The docstring from the parent.
        child_doc: Union[None, str]
            The docstring from the child.

        Returns
        -------
        Union[None, str]
            The merged docstring.
        """
    return merge_all_sections(parse_numpy_doc(prnt_doc), parse_numpy_doc(child_doc))
