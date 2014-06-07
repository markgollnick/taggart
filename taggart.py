"""Commander Taggart has saved us."""

import logging
import os

logger = logging.getLogger('taggart')
logger.setLevel(logging.WARNING)

THE_LIST = {}
SEPARATOR = '<==>'


def tag(file_name, tag_name, assert_exists=False):
    """Ah, they have a new Commander..."""
    if assert_exists and not os.path.exists(file_name):
        raise IOError('File "%s" not found!' % file_name)

    if tag_name in THE_LIST:
        if file_name not in THE_LIST[tag_name]:
            THE_LIST[tag_name].append(file_name)
    else:
        THE_LIST[tag_name] = [file_name]


def untag(file_name, tag_name):
    """I'm not the Commander."""
    if not tag_name in THE_LIST:
        return

    THE_LIST[tag_name] = list(set(THE_LIST[tag_name]) - set([file_name]))

    if not THE_LIST[tag_name]:
        del THE_LIST[tag_name]


def save(output_file, overwrite=False):
    """The mists of this planet are filling my head with such thoughts..."""
    if not overwrite and os.path.exists(output_file):
        raise IOError('File "%s" already exists!' % output_file)

    f = open(output_file, 'w')
    for tag_name, file_names in sorted(THE_LIST.items()):
        lines = [tag_name + SEPARATOR + file_name
                 for file_name in sorted(file_names)]
        f.write(os.linesep.join(lines) + os.linesep)
    f.close()


def load(input_file, overwrite=False, assert_exists=False):
    """It was cute when I didn't know you."""
    if not os.path.exists(input_file):
        raise IOError('File "%s" not found!' % input_file)

    if overwrite:
        global THE_LIST
        THE_LIST = {}

    f = open(input_file, 'r')
    for line in f.readlines():
        relationship = line.rstrip(os.linesep)
        tag_name, file_name = relationship.split(SEPARATOR, 1)  # :-(
        tag(file_name, tag_name, assert_exists)
    f.close()


def rename_tag(old_tag, new_tag):
    """And now, back after 18 years..."""
    if not old_tag in THE_LIST:
        return

    THE_LIST[new_tag] = THE_LIST[old_tag]
    del THE_LIST[old_tag]


def rename_file(old_file, new_file):
    """The ship was a model as big as this, a very clever deception indeed."""
    for tag_name, file_names in THE_LIST.items():
        if old_file in file_names:
            tag(new_file, tag_name)
            untag(old_file, tag_name)


def get_files_by_tag(tag):
    """Find them."""
    return sorted(THE_LIST.get(tag)) or []

# Alias
get_tag_files = get_files_by_tag


def get_tags_by_file(file_name):
    """FIIIIND THEEEEM."""
    tags = []
    for tag, file_names in THE_LIST.items():
        if file_name in file_names:
            tags.append(tag)
    return sorted(tags)

# Alias
get_file_tags = get_tags_by_file


def get_tags():
    return sorted(THE_LIST.keys())


def get_files():
    all_files = []
    for files in THE_LIST.values():
        all_files.extend(files)
    return sorted(set(all_files))
