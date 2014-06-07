"""Commander Taggart has saved us."""

import logging
import os

logger = logging.getLogger('taggart')
logger.setLevel(logging.WARNING)

THE_LIST = {}
SEPARATOR = '<==>'

TAG_TO_FILE = 'tag-->file'
FILE_TO_TAG = 'file-->tag'
FORMAT = TAG_TO_FILE


def tag(file_name, tag_name, assert_exists=False):
    """Ah, they have a new Commander..."""
    if assert_exists and not os.path.exists(file_name):
        raise IOError('File "%s" not found!' % file_name)

    if FORMAT == TAG_TO_FILE:
        if tag_name in THE_LIST:
            if file_name not in THE_LIST[tag_name]:
                THE_LIST[tag_name].append(file_name)
        else:
            THE_LIST[tag_name] = [file_name]

    else:
        if file_name in THE_LIST:
            if tag_name not in THE_LIST[file_name]:
                THE_LIST[file_name].append(tag_name)
        else:
            THE_LIST[file_name] = [tag_name]


def untag(file_name, tag_name):
    """I'm not the Commander."""
    if FORMAT == TAG_TO_FILE:
        if not tag_name in THE_LIST:
            return

        THE_LIST[tag_name] = list(set(THE_LIST[tag_name]) - set([file_name]))

        if not THE_LIST[tag_name]:
            del THE_LIST[tag_name]

    else:
        if not file_name in THE_LIST:
            return

        THE_LIST[file_name] = list(set(THE_LIST[file_name]) - set([tag_name]))

        if not THE_LIST[file_name]:
            del THE_LIST[file_name]


def save(output_file, overwrite=False):
    """The mists of this planet are filling my head with such thoughts..."""
    if not overwrite and os.path.exists(output_file):
        raise IOError('File "%s" already exists!' % output_file)

    f = open(output_file, 'w')

    for x, y in sorted(THE_LIST.items()):
        lines = [x + SEPARATOR + z for z in sorted(y)]
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
        x, y = relationship.split(SEPARATOR, 1)  # :-(

        if FORMAT == TAG_TO_FILE:
            tag_name, file_name = x, y
        else:
            file_name, tag_name = x, y

        tag(file_name, tag_name, assert_exists)
    f.close()


def rename_tag(old_tag, new_tag):
    """And now, back after 18 years..."""
    if FORMAT == TAG_TO_FILE:
        if not old_tag in THE_LIST:
            return

        THE_LIST[new_tag] = THE_LIST[old_tag]
        del THE_LIST[old_tag]

    else:
        for file_name, tag_names in THE_LIST.items():
            if old_tag in tag_names:
                tag(file_name, new_tag)
                untag(file_name, old_tag)


def rename_file(old_file, new_file):
    """The ship was a model as big as this, a very clever deception indeed."""
    if FORMAT == TAG_TO_FILE:
        for tag_name, file_names in THE_LIST.items():
            if old_file in file_names:
                tag(new_file, tag_name)
                untag(old_file, tag_name)

    else:
        if not old_file in THE_LIST:
            return

        THE_LIST[new_file] = THE_LIST[old_file]
        del THE_LIST[old_file]


def get_files_by_tag(tag_name):
    """Find them."""
    if FORMAT == TAG_TO_FILE:
        return sorted(THE_LIST.get(tag_name)) or []
    else:
        file_names = []
        for file_name, tag_names in THE_LIST.items():
            if tag_name in tag_names:
                file_names.append(file_name)
        return sorted(file_names)

# Alias
get_tag_files = get_files_by_tag


def get_tags_by_file(file_name):
    """FIIIIND THEEEEM."""
    if FORMAT == TAG_TO_FILE:
        tag_names = []
        for tag_name, file_names in THE_LIST.items():
            if file_name in file_names:
                tag_names.append(tag_name)
        return sorted(tag_names)
    else:
        return sorted(THE_LIST.get(file_name)) or []

# Alias
get_file_tags = get_tags_by_file


def get_tags():
    if FORMAT == TAG_TO_FILE:
        return sorted(THE_LIST.keys())
    else:
        all_tags = []
        for tags in THE_LIST.values():
            all_tags.extend(tags)
        return sorted(set(all_tags))


def get_files():
    if FORMAT == TAG_TO_FILE:
        all_files = []
        for files in THE_LIST.values():
            all_files.extend(files)
        return sorted(set(all_files))
    else:
        return sorted(THE_LIST.keys())
