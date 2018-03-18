

example = """
Introduction
============

This is some paragraph.

Should you have any question, any remark, or if you find a bug,
or if there is something you can do with the API but not with PyGithub,
please `open an issue <https://github.com/jacquev6/PyGithub/issues>`.

```python
res = {}
for item in self.items:
    if item.type == "data" and item.name == ttype:
        res[item.guid] = item.ddict
        key = "%s__%s" % (ttype, item.guid)
        self._dataCache[key] = item
return res
```

| Format   | Tag example |
| -------- | ----------- |
| Headings | =heading1=<br>==heading2==<br>===heading3=== |
| New paragraph | A blank line starts a new paragraph |
| Source code block |  // all on one line<br> {{{ if (foo) bar else   baz }}} |

# header 1

## header 2

(Very short) tutorial
---------------------

First create a Github instance::


Download and install
--------------------

This package is in the `Python Package Index <http://pypi.python.org/pypi/PyGithub>`__,
so ``easy_install PyGithub`` or ``pip install PyGithub`` should be enough.
You can also clone it on `Github <http://github.com/jacquev6/PyGithub>`__.

They talk about PyGithub
------------------------

* http://stackoverflow.com/questions/10625190/most-suitable-python-library-for-github-api-v3
    * http://stackoverflow.com/questions/12379637/django-social-auth-github-authentication
        * http://www.freebsd.org/cgi/cvsweb.cgi/ports/devel/py-pygithub/
* https://bugzilla.redhat.com/show_bug.cgi?id=910565

"""

