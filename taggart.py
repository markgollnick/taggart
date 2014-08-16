"""Introducing Taggart: The simple file tagger."""

import json
import logging
import os

# Initialize the logger
__DEBUG = False
__formatter = logging.Formatter(logging.BASIC_FORMAT)
__handler = logging.StreamHandler()
__handler.setFormatter(__formatter)
logger = logging.getLogger('taggart')
del logger.handlers[:]
logger.addHandler(__handler)
logger.setLevel(logging.WARNING if not __DEBUG else logging.DEBUG)

try:
    import yaml
except ImportError as e:
    logger.warn("PyYAML is not loaded. You will be able to save tag files in "
                "YAML format, but you will not be able to load them.")
    pass

# Store the list of files and tags in memory
THE_LIST = {}

# MEMORY MAPPING SETTING:
#   This allows you to use either "tags have files" or "files have tags" design
# paradigms, depending upon your desired application.
#   If you intend to refer to files by their tags more often than you intend to
# reference tags by their files, then you will probably want to use tag-to-file
# memory mapping, as it will be a lot faster in that case (this is the default
# setting). If you need to reference tags by their files more often, then you
# will probably want to use the file-to-tag memory mapping instead.
#   Either option you choose will result in a speed trade-off for the option
# that you didn't choose. Alas, such is the dilemma posed by "many-to-many"
# graph relationships such as file-tagging.
TAG_TO_FILE = 'tag-->file'
FILE_TO_TAG = 'file-->tag'
MAPPING = TAG_TO_FILE

# OUTPUT FORMAT SETTING:
# Available options are 'json', 'txt', and 'yaml'.
FORMAT = 'txt'

# Separator for plain text format
SEPARATOR = '<==>'


def tag(file_name, tag_name, assert_exists=False):
    """
    Add a single tag to a single file, optionally asserting file existence.

    @param file_name: Relative or absolute path to the file to tag
    @type file_name: str
    @param tag_name: The tag to apply to the file
    @type tag_name: str
    @param assert_exists: If True, don't tag nonexistent files
    @type assert_exists: bool
    @raise IOError: When assert_exists is True and file_name does not exist
    """
    if assert_exists and not os.path.exists(file_name):
        err = 'File "%s" not found!' % file_name
        logger.error(err)
        raise IOError(err)

    if MAPPING == TAG_TO_FILE:
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


def tags(file_names, tag_names, assert_exists=False):
    """
    Tag multiple files with multiple tags all at once.

    @param file_names: A file or a list of files to tag
    @type file_names: str or list
    @param tag_names: A tag or a list of tags to apply to the file or files
    @type tag_names: str or list
    @param assert_exists: If True, prevents tagging nonexistant files
    @type assert_exists: bool
    """
    logger.debug('Using %s memory mapping.' % MAPPING)

    if isinstance(file_names, basestring):
        file_names = [file_names]

    if isinstance(tag_names, basestring):
        tag_names = [tag_names]

    if len(file_names) <= len(tag_names):
        for file_name in file_names:
            for tag_name in tag_names:
                try:
                    tag(file_name, tag_name, assert_exists)
                except IOError as e:
                    logger.warn(e)
    else:
        for tag_name in tag_names:
            for file_name in file_names:
                try:
                    tag(file_name, tag_name, assert_exists)
                except IOError as e:
                    logger.warn(e)


def untag(file_name, tag_name):
    """
    Remove a single tag from a single file.

    @param file_name: The tagged file
    @type file_name: str
    @param tag_name: The tag to remove
    @type tag_name: str
    """
    if MAPPING == TAG_TO_FILE:
        if tag_name not in THE_LIST:
            return

        THE_LIST[tag_name] = list(set(THE_LIST[tag_name]) - set([file_name]))

        if not THE_LIST[tag_name]:
            del THE_LIST[tag_name]

    else:
        if file_name not in THE_LIST:
            return

        THE_LIST[file_name] = list(set(THE_LIST[file_name]) - set([tag_name]))

        if not THE_LIST[file_name]:
            del THE_LIST[file_name]


def untags(file_names, tag_names):
    """
    Remove multiple tags from multiple files all at once.

    @param file_names: A file or list of files from which to remove tags
    @type file_names: str or list
    @param tag_names: A tag or tags to remove from the file or files
    @type tag_names: str or list
    """
    logger.debug('Using %s memory mapping.' % MAPPING)

    if isinstance(file_names, basestring):
        file_names = [file_names]

    if isinstance(tag_names, basestring):
        tag_names = [tag_names]

    if len(file_names) <= len(tag_names):
        for file_name in file_names:
            for tag_name in tag_names:
                untag(file_name, tag_name)
    else:
        for tag_name in tag_names:
            for file_name in file_names:
                untag(file_name, tag_name)


def save(output_file, overwrite=True, fmt=FORMAT):
    """
    Save the list of tags to a file.

    @param output_file: The name of the file to save
    @type output_file: str
    @param overwrite: If True, overwrite the file if it exists
    @type overwrite: bool
    @param fmt: The format to save the output in: json, txt, or yaml
    @type fmt: str: 'json', 'txt', or 'yaml'
    @raise IOError: When overwrite is False and output_file already exists
    """
    logger.debug('Using %s memory mapping.' % MAPPING)

    if not overwrite and os.path.exists(output_file):
        err = 'File "%s" already exists!' % output_file
        logger.error(err)
        raise IOError(err)

    f = open(output_file, 'w')

    if fmt == 'json':
        f.write(json.dumps(THE_LIST, sort_keys=True))

    elif fmt == 'yaml':
        for x, y in sorted(THE_LIST.items()):
            lines = x + ':' + os.linesep
            lines += ('- ' + '{n}- '.join(sorted(y))).format(n=os.linesep)
            f.write(lines + os.linesep)

    else:
        if MAPPING == TAG_TO_FILE:
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


def load(input_file, overwrite=False, assert_exists=False, fmt=FORMAT):
    """
    Load a list of tags from a file.

    @param input_file: The name of the file to load
    @type input_file: str
    @param overwrite: If True, wipe the existing tag list in memory, if any.
                      If False, append to the existing tag list in memory.
    @type overwrite: bool
    @param assert_exists: If True, don't tag nonexistant files
    @type assert_exists: bool
    @param fmt: The format to save the output in: json, txt, or yaml
    @type fmt: str: 'json', 'txt', or 'yaml'
    @raise IOError: When input_file does not exist
    """
    if not os.path.exists(input_file):
        err = 'File "%s" not found!' % input_file
        logger.error(err)
        raise IOError(err)

    if overwrite:
        global THE_LIST
        THE_LIST = {}

    f = open(input_file, 'r')

    if fmt == 'json':
        THE_LIST.update({
            str(k): [
                str(s) for s in v] for k, v in json.loads(f.read()).items()
        })

    elif fmt == 'yaml':
        THE_LIST.update({
            str(k): [
                str(s) for s in v] for k, v in yaml.load(f.read()).items()
        })

    else:
        for line in f.readlines():
            relationship = line.rstrip(os.linesep)
            tag_name, file_name = relationship.split(SEPARATOR, 1)  # :-(
            tag(file_name, tag_name, assert_exists)

    f.close()


def rename_tag(old_tag, new_tag):
    """
    Rename a tag.

    Note that this renames a tag itself, not an application of a tag.
    Not a single instance of the old tag will remain applied to any file.

    @param old_tag: The old tag to rename
    @type old_tag: str
    @param new_tag: The new tag name to apply
    @type new_tag: str
    """
    logger.debug('Using %s memory mapping.' % MAPPING)

    if MAPPING == TAG_TO_FILE:
        if old_tag not in THE_LIST:
            return

        THE_LIST[new_tag] = THE_LIST.pop(old_tag)

    else:
        logger.info('Tag renaming operations may be slow for %s maps...' % (
            MAPPING))
        for file_name, tag_names in THE_LIST.items():
            if old_tag in tag_names:
                tag(file_name, new_tag)
                untag(file_name, old_tag)


def rename_file(old_file, new_file):
    """
    Rename a file.

    Note that this renames a file itself across all tags that may apply to it.

    @param old_file: The old file to rename
    @type old_file: str
    @param new_file: The new name of the file
    @type new_file: str
    """
    logger.debug('Using %s memory mapping.' % MAPPING)

    if MAPPING == TAG_TO_FILE:
        logger.info('File rename operations may be slow for %s maps...' % (
            MAPPING))
        for tag_name, file_names in THE_LIST.items():
            if old_file in file_names:
                tag(new_file, tag_name)
                untag(old_file, tag_name)

    else:
        if old_file not in THE_LIST:
            return

        THE_LIST[new_file] = THE_LIST[old_file]
        del THE_LIST[old_file]


def get_files_by_tag(tag_name):
    """
    Given a tag, get all files associated with that tag.

    @param tag_name: The name of the tag to query on
    @type tag_name: str
    @return: A list of associated file names
    @rtype: list of str
    """
    logger.debug('Using %s memory mapping.' % MAPPING)

    if MAPPING == TAG_TO_FILE:
        return sorted(THE_LIST.get(tag_name)) or []
    else:
        logger.info('Queries by tag may be slow for %s maps...' % MAPPING)
        file_names = []
        for file_name, tag_names in THE_LIST.items():
            if tag_name in tag_names:
                file_names.append(file_name)
        return sorted(file_names)

# Alias
get_tag_files = get_files_by_tag


def get_tags_by_file(file_name):
    """
    Given a file, get all tags associated with that file.

    @param file_name: The name of the file to query on
    @type file_name: str
    @return: A list of assocaited tag names
    @rtype: list of str
    """
    logger.debug('Using %s memory mapping.' % MAPPING)

    if MAPPING == TAG_TO_FILE:
        logger.info('Queries by file may be slow for %s maps...' % MAPPING)
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
    """Self-explanatory: Get all tags currently in memory."""
    logger.debug('Using %s memory mapping.' % MAPPING)

    if MAPPING == TAG_TO_FILE:
        return sorted(THE_LIST.keys())
    else:
        logger.info('Exhaustive tag obtainment may be slow for %s maps...' % (
            MAPPING))
        all_tags = []
        for tags in THE_LIST.values():
            all_tags.extend(tags)
        return sorted(set(all_tags))


def get_files():
    """Self-explanatory: Get all files with tags currently stored in memory."""
    logger.debug('Using %s memory mapping.' % MAPPING)

    if MAPPING == TAG_TO_FILE:
        logger.info('Exhaustive file obtainment may be slow for %s maps...' % (
            MAPPING))
        all_files = []
        for files in THE_LIST.values():
            all_files.extend(files)
        return sorted(set(all_files))
    else:
        return sorted(THE_LIST.keys())
