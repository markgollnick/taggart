"""Commander Taggart has saved us."""

import logging
import os

__DEBUG = False
__formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
__handler = logging.StreamHandler()
__handler.setFormatter(__formatter)
logger = logging.getLogger('taggart')
logger.addHandler(__handler)
logger.setLevel(logging.WARNING if not __DEBUG else logging.DEBUG)

THE_LIST = {}
SEPARATOR = '<==>'

TAG_TO_FILE = 'tag-->file'
FILE_TO_TAG = 'file-->tag'
FORMAT = TAG_TO_FILE


def tag(file_name, tag_name, assert_exists=False):
    """Ah, they have a new Commander..."""
    logger.debug('Using %s memory mapping.' % FORMAT)

    if assert_exists and not os.path.exists(file_name):
        err = 'File "%s" not found!' % file_name
        logger.warn(err)
        raise IOError(err)

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
    logger.debug('Using %s memory mapping.' % FORMAT)

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
    logger.debug('Using %s memory mapping.' % FORMAT)

    if not overwrite and os.path.exists(output_file):
        err = 'File "%s" already exists!' % output_file
        logger.warn(err)
        raise IOError(err)

    f = open(output_file, 'w')

    if FORMAT == TAG_TO_FILE:
        for tag_name, file_names in sorted(THE_LIST.items()):
            lines = [tag_name + SEPARATOR + file_name
                     for file_name in sorted(file_names)]
            f.write(os.linesep.join(lines) + os.linesep)
    else:
        for file_name, tag_names in sorted(THE_LIST.items()):
            lines = [tag_name + SEPARATOR + file_name
                     for tag_name in sorted(tag_names)]
            f.write(os.linesep.join(lines) + os.linesep)

    f.close()


def load(input_file, overwrite=False, assert_exists=False):
    """It was cute when I didn't know you."""
    if not os.path.exists(input_file):
        err = 'File "%s" not found!' % input_file
        logger.warn(err)
        raise IOError(err)

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
    logger.debug('Using %s memory mapping.' % FORMAT)

    if FORMAT == TAG_TO_FILE:
        if not old_tag in THE_LIST:
            return

        THE_LIST[new_tag] = THE_LIST.pop(old_tag)

    else:
        logger.info('Tag renaming operations may be slow for %s maps...' % (
            FORMAT))
        for file_name, tag_names in THE_LIST.items():
            if old_tag in tag_names:
                tag(file_name, new_tag)
                untag(file_name, old_tag)


def rename_file(old_file, new_file):
    """The ship was a model as big as this, a very clever deception indeed."""
    logger.debug('Using %s memory mapping.' % FORMAT)

    if FORMAT == TAG_TO_FILE:
        logger.info('File rename operations may be slow for %s maps...' % (
            FORMAT))
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
    logger.debug('Using %s memory mapping.' % FORMAT)

    if FORMAT == TAG_TO_FILE:
        return sorted(THE_LIST.get(tag_name)) or []
    else:
        logger.info('Queries by tag may be slow for %s maps...' % FORMAT)
        file_names = []
        for file_name, tag_names in THE_LIST.items():
            if tag_name in tag_names:
                file_names.append(file_name)
        return sorted(file_names)

# Alias
get_tag_files = get_files_by_tag


def get_tags_by_file(file_name):
    """FIIIIND THEEEEM."""
    logger.debug('Using %s memory mapping.' % FORMAT)

    if FORMAT == TAG_TO_FILE:
        logger.info('Queries by file may be slow for %s maps...' % FORMAT)
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
    """Self-explanatory."""
    logger.debug('Using %s memory mapping.' % FORMAT)

    if FORMAT == TAG_TO_FILE:
        return sorted(THE_LIST.keys())
    else:
        logger.info('Exhaustive tag obtainment may be slow for %s maps...' % (
            FORMAT))
        all_tags = []
        for tags in THE_LIST.values():
            all_tags.extend(tags)
        return sorted(set(all_tags))


def get_files():
    """Self-explanatory."""
    logger.debug('Using %s memory mapping.' % FORMAT)

    if FORMAT == TAG_TO_FILE:
        logger.info('Exhaustive file obtainment may be slow for %s maps...' % (
            FORMAT))
        all_files = []
        for files in THE_LIST.values():
            all_files.extend(files)
        return sorted(set(all_files))
    else:
        return sorted(THE_LIST.keys())
