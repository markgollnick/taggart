Taggart
=======

Taggart is a simple file-tagging aid.


Usage
-----

Simple interface:

    $ python -i
    >>> import taggart
    >>> taggart.load('tags.txt')
    >>> taggart.tag('EE230/hw07.md', 'EE 230')
    >>> taggart.tag('EE230/hw07.md', 'Markdown')
    >>> taggart.tag('EE230/hw07.pdf', 'EE 230')
    >>> taggart.tag('EE230/hw07.pdf', 'Rendered')
    >>> taggart.save('tags.txt', overwrite=True)
    >>> exit()

Human readable:

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

Easy queries:

    $ grep "EE 230" tags.txt
    EE 230<==>EE230/hw07.md
    EE 230<==>EE230/hw07.pdf

Advanced queries:

    $ awk '/EE 2[0-9]+/ { split($0, a, "<==>"); print a[2] }' tags.txt
    EE201/final.md
    EE201/final.pdf
    EE230/hw07.md
    EE230/hw07.pdf


Testing
-------

Taggart is built with Travis CI and is WOMM Certified™.

Master branch: [![Build Status](https://travis-ci.org/markgollnick/taggart.svg?branch=master)](https://travis-ci.org/markgollnick/taggart)

![WOMM Certified™](http://content.screencast.com/users/markgollnick/folders/Jing/media/19ea7b38-4a94-450c-9190-3e5115ebe1c4/womm.png)


License
-------

Boost Software License, Version 1.0: <http://www.boost.org/LICENSE_1_0.txt>
