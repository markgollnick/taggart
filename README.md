Taggart
=======

[![Build Status](https://travis-ci.org/markgollnick/taggart.svg?branch=master)](https://travis-ci.org/markgollnick/taggart)
[![Coverage Status](https://img.shields.io/coveralls/markgollnick/taggart.svg)](https://coveralls.io/r/markgollnick/taggart)

Taggart is a simple yet robust file-tagging aid.

![Taggart](http://content.screencast.com/users/markgollnick/folders/Jing/media/25f679d2-bece-4324-841b-86adaf408e33/taggart.png)


Usage
-----

Easy installation:

    $ pip install git+ssh://git@github.com/markgollnick/taggart@v1.4.0#egg=taggart-1.4.0

Simple interface:

    >>> import taggart

You may tag files one-at-a-time:

    >>> taggart.tag('homework.md', 'Markdown')
    >>> taggart.tag('homework.pdf', 'Rendered')

…or you may tag multiple files, or apply multiple tags…

    >>> taggart.tag(['homework.md', 'homework.pdf'], 'Homework')
    >>> taggart.tag('vacation/photos', ['Vacation', 'Photos'])
    >>> taggart.tag('vacation/budget', ['Vacation', 'Finances'])

…or you may do both at the same time:

    >>> taggart.tag(['vacation/photos', 'wedding'], ['Photos', 'Memories'])

Save the results:

    >>> taggart.save('tags.txt')

…using a variety of formats:

    >>> taggart.save('tags.json')
    >>> taggart.save('tags.yaml')

You can also load from a backup:

    >>> taggart.load('tags.txt')

…but you don’t have to write anything to disk at all, if you don’t want to:

- `taggart.dump()` … `taggart.dump_json()` … `taggart.dump_yaml()`

You also don’t have to load anything form disk, either, if you already have the
data you need from somewhere else (represented as string `s`):

- `taggart.init(s, fmt=…)`, where `fmt` is `'text'`, `'json'`, or `'yaml'`.

That should cover the basics. Happy tagging!


Reference
---------

* `tag()` — Tag one (or more) file(s) with one (or more) tag(s)
* `untag()` — Remove one (or more) tag(s) from one (or more) file(s)
* `dump()` — Dump tags using a variety of formats (memory -> stdout)
* `save()` — Save tags using a variety of formats (memory -> hdd)
* `parse()` — Read tags from a variety of string formats (stdin -> stdout)
* `init()` — Load tags from a variety of string formats (stdin -> memory)
* `load()` — Load tags from a variety of file formats (hdd -> memory)
* `remap()` — Don’t use unless you know what you’re doing; see below
* `rename_tag()` — Exhaustively rename every occurrence of a tag
* `rename_file()` — Exhaustively rename every occurrence of a file
* `get_files_by_tag()` — Get all files tagged with the given tag
* `get_tags_by_file()` — Get all tags applied to the given file
* `get_tags()` — Get all tags currently applied with Taggart
* `get_files()` — Get all files that are currently tagged with Taggart tags


Advanced Usage
--------------

**Optimizing Memory**

By default, Taggart maps tags to files, (not files to tags,) meaning that a
file may occur multiple times in memory. Consider the following:

    >>> import taggart
    >>> taggart.tag(['vacation/photos', 'wedding'], ['Photos', 'Memories'])
    >>> taggart.save('tags.yaml')
    >>> exit()

    $ cat tags.yaml
    Memories:
    - vacation/photos
    - wedding
    Photos:
    - vacation/photos
    - wedding

This may seem backwards, but actually, this is probably the ideal for most
applications, as the general goal of tagging is to apply a tag to a file and
use it to reference that file (and others) many times later on. In Taggart’s
implementation of file-tagging, instead of “applying a tag to a file,” we
actually apply the *file* to the *tag*, since referencing files by their tags
is far easier and *much* faster than scanning through a huge list of files with
many irrelevant tags just to see which files actually have the tag you’re
searching for.

Consider, for a moment, Mac OS X, and its implementation of file-tagging. After
tagging many files with a certain tag, say you want to change the tag’s color.
Have you ever tried to change the colored dot of a tag that happens to be
applied to many, many files? See how long it takes? That’s because, as far as
Mac OS X is concerned, “files have tags”… and every single one of those tags,
*plural,* now needs to be updated because you changed *one* of them.

This design assumes that most users will want to use a few tags for potentially
many files. Even if the tag-to-file ratio ends up being close to or greater
than 1.0, we still have the added benefit of a faster query-by-tag speed, which
is probably what most users will want. However, if your application intends to
apply many tags to a potentially very small set of files, it may actually be
better for you to do as Mac OS X does, and reference tags by their files (aka
“file-to-tag mapping”) rather than files by their tags (aka “tag-to-file
mapping”, which is the default setting). Taggart makes this transition easy:

    >>> import taggart
    >>> taggart.load('tags.yaml')
    >>> taggart.remap(taggart.FILE_TO_TAG)
    >>> taggart.save('new_tags.yaml')
    >>> exit()

    $ cat new_tags.yaml
    vacation/photos:
    - Memories
    - Photos
    wedding:
    - Memories
    - Photos

Note that `taggart.remap()` may be a very slow operation, depending on how many
files/tags Taggart needs to remap. You may check Taggart’s current memory map
setting by checking the `taggart.MAPPING` value, and if you wish, you may even
explicitly set it after loading Taggart, with the `taggart.TAG_TO_FILE` and/or
the `taggart.FILE_TO_TAG` values. Also, when using the alternate mapping, note
that the plain text output format is unaffected (on each line, tags will always
appear first, files second) so you can use that as a transitionary back-up
format should you need it. However, the JSON and YAML formats (as shown above)
*will* swap their keys and their values, as is appropriate. This means that you
should NOT attempt to load a back-up JSON or YAML file that was generated while
Taggart was using a different memory-mapping scheme than that of the currently
loaded instance, as it will pollute the tag-map with files where there should
be tags, and tags where there should be files.

For more information on which of these two mapping styles you should use, see
the documentation in `taggart.py`, or set Taggart’s logger to `INFO` while your
application is running, and see if you encounter any messages about slow
computations. For most folks, the default setting of tag-to-file mapping is
probably the ideal setting, and remapping shouldn’t be necessary, but the
option is there should you need it.

Good luck!


Testing
-------

1.  Requirements:

    - Python 2.7, 3.2, 3.3, or 3.4
    - Pip >= 1.4.1
    - virtualenv
    - virtualenvwrapper
    - ant >= 1.8.4

2.  Run the following:

        $ ant bootstrap
        $ workon taggart
        $ ant test

It’s that simple.

[![WOMM Certified™](http://content.screencast.com/users/markgollnick/folders/Jing/media/19ea7b38-4a94-450c-9190-3e5115ebe1c4/womm.png)](http://blog.codinghorror.com/the-works-on-my-machine-certification-program/)


License
-------

Boost Software License, Version 1.0: <http://www.boost.org/LICENSE_1_0.txt>
