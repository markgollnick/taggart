Taggart
=======

![Taggart](http://content.screencast.com/users/markgollnick/folders/Jing/media/31dd044b-f409-439d-947b-c9baa0499800/taggart.png)

Taggart is a simple yet robust file-tagging aid.


Usage
-----

Easy installation:

    $ pip install https://github.com/markgollnick/taggart/releases/download/v1.2.0/taggart-1.2.0.tar.gz

Simple interface:

    >>> import taggart

Tag files one-at-a-time:

    >>> taggart.tag('EE230/hw07.md', 'Markdown')
    >>> taggart.tag('EE230/hw07.pdf', 'Rendered')

…or tag multiple files at once:

    >>> taggart.tags(['EE230/hw07.md', 'EE230/hw07.pdf'], 'EE 230')

…or apply multiple tags at once:

    >>> taggart.tags('EE201/final.md', ['EE 201', 'Markdown'])
    >>> taggart.tags('EE201/final.pdf', ['EE 201', 'Rendered'])

…or both:

    >>> taggart.tags(['EE201/final.md', 'EE201/final.pdf'], ['EE 201', 'Final'])

Save the results:

    >>> taggart.save('tags.txt')

…using a variety of formats:

    >>> taggart.save('tags.json')
    >>> taggart.save('tags.yaml')

…such as plain text (easiest to query with awk or grep):

    $ cat tags.txt
    EE 201<==>EE201/final.md
    EE 201<==>EE201/final.pdf
    EE 230<==>EE230/hw07.md
    EE 230<==>EE230/hw07.pdf
    Final<==>EE201/final.md
    Final<==>EE201/final.pdf
    Markdown<==>EE201/final.md
    Markdown<==>EE230/hw07.md
    Rendered<==>EE201/final.pdf
    Rendered<==>EE230/hw07.pdf

…or JSON (easiest to parse):

    $ cat tags.json | json_pp
    {
       "EE 230" : [
          "EE230/hw07.md",
          "EE230/hw07.pdf"
       ],
       "EE 201" : [
          "EE201/final.md",
          "EE201/final.pdf"
       ],
       "Rendered" : [
          "EE230/hw07.pdf",
          "EE201/final.pdf"
       ],
       "Markdown" : [
          "EE230/hw07.md",
          "EE201/final.md"
       ],
       "Final" : [
          "EE201/final.md",
          "EE201/final.pdf"
       ]
    }

…or YAML (easiest to read):

    $ cat tags.yaml
    EE 201:
    - EE201/final.md
    - EE201/final.pdf
    EE 230:
    - EE230/hw07.md
    - EE230/hw07.pdf
    Final:
    - EE201/final.md
    - EE201/final.pdf
    Markdown:
    - EE201/final.md
    - EE230/hw07.md
    Rendered:
    - EE201/final.pdf
    - EE230/hw07.pdf

…but you don't have to write anything to disk at all if you don't want to:

- `taggart.dump()` … `taggart.dump_json()` … `taggart.dump_yaml()`

You also don't have to load anything form disk, either, if you already have the
data you need from somewhere else (represented as `s`):

- `taggart.parse(s)` … `taggart.parse_json(s)` … `taggart.parse_yaml(s)`

Server crashed? Lost all your tags that were in-memory? No worries. Assuming
you make periodic backups (you should), Taggart’s got you covered:

- `taggart.load('tags.txt')` …
  `taggart.load('tags.json')` …
  `taggart.load('tags.yaml')`


Advanced Usage
--------------

If you get to tagging many, many, MANY files, depending on your application, it
may be more beneficial for you (in computational terms) to reference tags by
their files (aka "file-to-tag mapping") rather than files by their tags (aka
"tag-to-file mapping", which is the default setting). Taggart makes this easy:

    >>> import taggart
    >>> taggart.MAPPING = taggart.FILE_TO_TAG
    >>> taggart.load('tags.txt', overwrite=True)
    >>> taggart.save('new_tags.yaml')
    >>> exit()

    $ cat new_tags.yaml
    EE201/final.md:
    - EE 201
    - Final
    - Markdown
    EE201/final.pdf:
    - EE 201
    - Final
    - Rendered
    EE230/hw07.md:
    - EE 230
    - Markdown
    EE230/hw07.pdf:
    - EE 230
    - Rendered

Note that when using the alternate mapping, the plain text format is unaffected
(on each line, tags will always appear first, files second) so you can easily
use that as a transitionary format. However, the JSON and YAML formats *will*
swap their keys and their values, as is appropriate. For more information on
which of these two mapping styles you should use, see the documentation in
`taggart.py`, or set taggart's logger to `INFO` while your application is using
taggart, and see if you encounter any messages about slow computations.

If the need is great enough, you can even swap between these two memory-mapping
formats without ever having to write anything to disk (this may be a very
expensive operation, depending on how many files and tags you have):

    >>> taggart.remap()

For most folks, however, the default setting of tag-to-file mapping is probably
the ideal option, and remapping shouldn’t be necessary.

Good luck!


Testing
-------

[![Build Status](https://travis-ci.org/markgollnick/taggart.svg?branch=master)](https://travis-ci.org/markgollnick/taggart)
[![Coverage Status](https://img.shields.io/coveralls/markgollnick/taggart.svg)](https://coveralls.io/r/markgollnick/taggart)

[![WOMM Certified™](http://content.screencast.com/users/markgollnick/folders/Jing/media/19ea7b38-4a94-450c-9190-3e5115ebe1c4/womm.png)](http://blog.codinghorror.com/the-works-on-my-machine-certification-program/)


License
-------

Boost Software License, Version 1.0: <http://www.boost.org/LICENSE_1_0.txt>
