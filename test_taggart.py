import copy
import sys
from unittest import TestCase

from mock import call, patch

import taggart


class ImportErrorTestCase(TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.real_import = __import__

        def import_error(name, *args, **kwargs):
            if name == 'yaml':
                raise ImportError
            return self.real_import(name, *args, **kwargs)

        self.import_patch = patch(
            target='__builtin__.__import__', new=import_error)

        self.import_mock = self.import_patch.start()

    def tearDown(self):
        patch.stopall()
        reload(taggart)

    def test_yaml_import_errors_out_gracefully(self):
        self.assertTrue(hasattr(taggart, 'yaml'))
        del sys.modules['yaml']
        del taggart.yaml
        self.assertFalse(hasattr(taggart, 'yaml'))
        reload(taggart)
        self.assertFalse(hasattr(taggart, 'yaml'))


class BaseCase(TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.open_mock = patch('__builtin__.open').start()
        self.file_mock = self.open_mock.return_value
        self.exists_mock = patch.object(taggart.os.path, 'exists').start()

        self.exists_mock.return_value = True


class Taggart_TTF_BaseCase(BaseCase):
    def setUp(self):
        super(Taggart_TTF_BaseCase, self).setUp()
        reload(taggart)
        taggart.logger.setLevel('CRITICAL')
        taggart.MAPPING = taggart.TAG_TO_FILE
        taggart.THE_LIST = {
            'Tag A': ['file_1'],
            'Tag B': ['file_2', 'file_3'],
            'Tag C': ['file_2', 'file_3'],
            'Tag D': ['file_3']
        }


class Taggart_FTT_BaseCase(BaseCase):
    def setUp(self):
        super(Taggart_FTT_BaseCase, self).setUp()
        reload(taggart)
        taggart.logger.setLevel('CRITICAL')
        taggart.MAPPING = taggart.FILE_TO_TAG
        taggart.THE_LIST = {
            'file_1': ['Tag A'],
            'file_2': ['Tag B', 'Tag C'],
            'file_3': ['Tag B', 'Tag C', 'Tag D']
        }


class tag_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_tag_assert_exists(self):
        self.exists_mock.return_value = False
        self.assertRaises(
            IOError, taggart.tag, 'new_file', 'New Tag', assert_exists=True)
        self.exists_mock.assert_called_once_with('new_file')

    def test_tag(self):
        taggart.tag('new_file', 'New Tag')
        taggart.tag('other_file', 'New Tag')
        self.assertEqual(
            ['new_file', 'other_file'], taggart.THE_LIST.get('New Tag'))


class tag_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_tag(self):
        taggart.tag('new_file', 'New Tag')
        taggart.tag('new_file', 'Other Tag')
        self.assertEqual(
            ['New Tag', 'Other Tag'], taggart.THE_LIST.get('new_file'))


class tags_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_tags_works_with_strings(self):
        taggart.tags('new_file', 'New Tag')
        self.assertEqual(['new_file'], taggart.THE_LIST.get('New Tag'))

    @patch.object(taggart, 'logger')
    def test_tags_warns_on_nonexistance(self, log_mock):
        self.exists_mock.return_value = False
        taggart.tags('new_file', 'New Tag', assert_exists=True)
        self.exists_mock.assert_called_once_with('new_file')
        self.assertEqual(None, taggart.THE_LIST.get('New Tag'))
        self.assertEqual(1, log_mock.warn.call_count)

    @patch.object(taggart, 'logger')
    def test_tags_called_with_many_files_and_tags(self, log_mock):
        self.exists_mock.return_value = None
        # TODO: This needs to be optimized.
        self.exists_mock.side_effect = [True, False, True, True, False, True]
        taggart.tags(['a', 'b', 'c'], ['A', 'B'], assert_exists=True)
        self.assertEqual(6, self.exists_mock.call_count)
        self.exists_mock.assert_has_calls([
            call('a'), call('b'), call('c'),
            call('a'), call('b'), call('c')
        ])
        self.assertEqual(['a', 'c'], taggart.THE_LIST.get('A'))
        self.assertEqual(['a', 'c'], taggart.THE_LIST.get('B'))
        self.assertEqual(2, log_mock.warn.call_count)


class untag_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_untag_nonexistent_tag(self):
        taggart.untag('new_file', 'New Tag')
        self.assertEqual(None, taggart.THE_LIST.get('New Tag'))

    def test_untag_only_file_for_tag(self):
        taggart.untag('file_1', 'Tag A')
        self.assertEqual(None, taggart.THE_LIST.get('Tag A'))
        self.assertEqual(
            ['Tag B', 'Tag C', 'Tag D'], sorted(list(taggart.THE_LIST.keys())))


class untag_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_untag_nonexistent_file(self):
        taggart.untag('new_file', 'New Tag')
        self.assertEqual(None, taggart.THE_LIST.get('new_file'))

    def test_untag_only_tag_for_file(self):
        taggart.untag('file_1', 'Tag A')
        self.assertEqual(None, taggart.THE_LIST.get('file_1'))
        self.assertEqual(
            ['file_2', 'file_3'], sorted(list(taggart.THE_LIST.keys())))


class untags_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_untags_works_with_strings(self):
        taggart.untags('file_3', 'Tag C')
        self.assertEqual(['file_2'], taggart.THE_LIST.get('Tag C'))

    def test_untags_called_with_many_files_and_tags(self):
        taggart.untags(['file_1', 'file_2', 'file_3'], ['Tag B', 'Tag C'])
        self.assertEqual({
            'Tag A': ['file_1'],
            'Tag D': ['file_3']
        }, taggart.THE_LIST)


class dump_json_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_dump_json(self):
        expect = (
            '{"Tag A": ["file_1"],'
            ' "Tag B": ["file_2", "file_3"],'
            ' "Tag C": ["file_2", "file_3"],'
            ' "Tag D": ["file_3"]}')
        self.assertEqual(expect, taggart.dump_json())


class dump_json_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_dump_json(self):
        expect = (
            '{"file_1": ["Tag A"],'
            ' "file_2": ["Tag B", "Tag C"],'
            ' "file_3": ["Tag B", "Tag C", "Tag D"]}')
        self.assertEqual(expect, taggart.dump_json())


class dump_text_BaseCase(BaseCase):
    def setUp(self):
        super(dump_text_BaseCase, self).setUp()
        self.sorted_output = """Tag A<==>file_1
Tag B<==>file_2
Tag B<==>file_3
Tag C<==>file_2
Tag C<==>file_3
Tag D<==>file_3
"""


class dump_text_TTF_TestCase(dump_text_BaseCase, Taggart_TTF_BaseCase):
    def test_dump_text(self):
        self.assertEqual(self.sorted_output, taggart.dump_text(sort=False))
        self.assertEqual(self.sorted_output, taggart.dump_text(sort=True))


class dump_text_FTT_TestCase(dump_text_BaseCase, Taggart_FTT_BaseCase):
    def test_dump_text(self):
        unsorted_output = """Tag A<==>file_1
Tag B<==>file_2
Tag C<==>file_2
Tag B<==>file_3
Tag C<==>file_3
Tag D<==>file_3
"""
        self.assertEqual(unsorted_output, taggart.dump_text(sort=False))
        self.assertEqual(self.sorted_output, taggart.dump_text(sort=True))


class dump_yaml_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_dump_yaml(self):
        expect = """Tag A:
- file_1
Tag B:
- file_2
- file_3
Tag C:
- file_2
- file_3
Tag D:
- file_3
"""
        self.assertEqual(expect, taggart.dump_yaml())


class dump_yaml_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_dump_yaml(self):
        expect = """file_1:
- Tag A
file_2:
- Tag B
- Tag C
file_3:
- Tag B
- Tag C
- Tag D
"""
        self.assertEqual(expect, taggart.dump_yaml())


class dump_TestCase(BaseCase):
    @patch.object(taggart, 'dump_json')
    def test_dump_json(self, json_mock):
        result = taggart.dump('json')
        self.assertIs(result, json_mock.return_value)

    @patch.object(taggart, 'dump_yaml')
    def test_dump_yaml(self, yaml_mock):
        result = taggart.dump('yaml')
        self.assertIs(result, yaml_mock.return_value)

    @patch.object(taggart, 'dump_text')
    def test_dump_text(self, text_mock):
        result = taggart.dump('text')
        self.assertIs(result, text_mock.return_value)


class save_TestCase(BaseCase):
    def test_save_rasies_error_when_file_exists_without_overwrite(self):
        self.exists_mock.return_value = True
        self.assertRaises(IOError, taggart.save, 'output.txt', overwrite=False)

    @patch.object(taggart, 'dump')
    def test_save_success(self, dump_mock):
        dump_mock.return_value = 'success'
        taggart.save('output.txt')
        dump_mock.assert_called_once_with('text')
        self.open_mock.assert_called_once_with('output.txt', 'w')
        self.file_mock.write.assert_called_once_with('success')
        self.file_mock.close.assert_called_once_with()


class parse_json_TestCase(BaseCase):
    def test_parse_json(self):
        expect = {'New Tag': ['a_file'], 'Other Tag': ['a_file', 'b_file']}
        input = '{"New Tag": ["a_file"], "Other Tag": ["a_file", "b_file"]}'
        self.assertEqual(expect, taggart.parse_json(input))


class parse_text_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_parse_text(self):
        expect = {'New Tag': ['a_file'], 'Other Tag': ['a_file', 'b_file']}
        input = 'New Tag<==>a_file\nOther Tag<==>a_file\nOther Tag<==>b_file'
        self.assertEqual(expect, taggart.parse_text(input))


class parse_text_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_parse_text(self):
        expect = {'a_file': ['New Tag', 'Other Tag'], 'b_file': ['Other Tag']}
        input = 'New Tag<==>a_file\nOther Tag<==>a_file\nOther Tag<==>b_file'
        self.assertEqual(expect, taggart.parse_text(input))


class parse_yaml_TestCase(BaseCase):
    def test_parse_yaml(self):
        expect = {'New Tag': ['a_file'], 'Other Tag': ['a_file', 'b_file']}
        input = 'New Tag:\n-  a_file\nOther Tag:\n-  a_file\n-  b_file'
        self.assertEqual(expect, taggart.parse_yaml(input))


class parse_TestCase(BaseCase):
    @patch.object(taggart, 'parse_json')
    def test_parse_json(self, json_mock):
        result = taggart.parse('data', 'json')
        json_mock.assert_called_once_with('data')
        self.assertIs(result, json_mock.return_value)

    @patch.object(taggart, 'parse_yaml')
    def test_parse_yaml(self, yaml_mock):
        result = taggart.parse('data', 'yaml')
        yaml_mock.assert_called_once_with('data')
        self.assertIs(result, yaml_mock.return_value)

    @patch.object(taggart, 'parse_text')
    def test_parse_text(self, text_mock):
        result = taggart.parse('data', 'text')
        text_mock.assert_called_once_with('data')
        self.assertIs(result, text_mock.return_value)


class load_TestCase(BaseCase):
    def test_load_rasies_error_for_nonexistent_file(self):
        self.exists_mock.return_value = False
        self.assertRaises(IOError, taggart.load, 'input.txt')

    @patch.object(taggart, 'parse')
    def test_load_success(self, parse_mock):
        parse_mock.return_value = {'result': 'success'}
        taggart.THE_LIST = {'preexisting': 'condition'}
        taggart.load('input.txt')
        self.open_mock.assert_called_once_with('input.txt', 'r')
        self.file_mock.read.assert_called_once_with()
        self.file_mock.close.assert_called_once_with()
        parse_mock.assert_called_once_with(
            self.file_mock.read.return_value, 'text')
        self.assertEqual(
            {'preexisting': 'condition', 'result': 'success'},
            taggart.THE_LIST)

    @patch.object(taggart, 'parse')
    def test_load_with_clean_slate_success(self, parse_mock):
        parse_mock.return_value = {'result': 'success'}
        taggart.THE_LIST = {'preexisting': 'condition'}
        taggart.load('input.txt', overwrite=True)
        self.open_mock.assert_called_once_with('input.txt', 'r')
        self.file_mock.read.assert_called_once_with()
        self.file_mock.close.assert_called_once_with()
        parse_mock.assert_called_once_with(
            self.file_mock.read.return_value, 'text')
        self.assertEqual({'result': 'success'}, taggart.THE_LIST)


class remap_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_remap(self):
        taggart.remap()
        self.assertEqual({
            'file_1': ['Tag A'],
            'file_2': ['Tag B', 'Tag C'],
            'file_3': ['Tag B', 'Tag C', 'Tag D']
        }, taggart.THE_LIST)


class remap_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_remap(self):
        taggart.remap()
        self.assertEqual({
            'Tag A': ['file_1'],
            'Tag B': ['file_2', 'file_3'],
            'Tag C': ['file_2', 'file_3'],
            'Tag D': ['file_3']
        }, taggart.THE_LIST)


class rename_tag_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_rename_nonexistent_tag(self):
        original = copy.deepcopy(taggart.THE_LIST)
        taggart.rename_tag('Nonexistent Tag', 'Existent Tag')
        self.assertIsNot(original, taggart.THE_LIST)
        self.assertEqual(original, taggart.THE_LIST)

    def test_rename_tag(self):
        taggart.rename_tag('Tag B', 'Cool B')
        self.assertEqual({
            'Tag A': ['file_1'],
            'Cool B': ['file_2', 'file_3'],
            'Tag C': ['file_2', 'file_3'],
            'Tag D': ['file_3']
        }, taggart.THE_LIST)


class rename_tag_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_rename_tag(self):
        taggart.rename_tag('Tag B', 'Cool B')
        self.assertEqual({
            'file_1': ['Tag A'],
            'file_2': ['Tag C', 'Cool B'],
            'file_3': ['Tag D', 'Tag C', 'Cool B']
        }, taggart.THE_LIST)


class rename_file_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_rename_file(self):
        taggart.rename_file('file_2', '2_cool')
        self.assertEqual({
            'Tag A': ['file_1'],
            'Tag B': ['2_cool', 'file_3'],
            'Tag C': ['2_cool', 'file_3'],
            'Tag D': ['file_3']
        }, taggart.THE_LIST)


class rename_file_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_rename_nonexistent_file(self):
        original = copy.deepcopy(taggart.THE_LIST)
        taggart.rename_file('nonexistent_file', 'existent_file')
        self.assertIsNot(original, taggart.THE_LIST)
        self.assertEqual(original, taggart.THE_LIST)

    def test_rename_file(self):
        taggart.rename_file('file_2', '2_cool')
        self.assertEqual({
            'file_1': ['Tag A'],
            'file_3': ['Tag B', 'Tag C', 'Tag D'],
            '2_cool': ['Tag B', 'Tag C']
        }, taggart.THE_LIST)


class get_files_by_tag_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_get_files_by_tag(self):
        self.assertEquals(
            ['file_2', 'file_3'], taggart.get_files_by_tag('Tag B'))


class get_files_by_tag_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_get_files_by_tag(self):
        self.assertEquals(
            ['file_2', 'file_3'], taggart.get_files_by_tag('Tag B'))


class get_tag_files_alias_TestCase(BaseCase):
    def test_get_tag_files_alias(self):
        self.assertIs(taggart.get_tag_files, taggart.get_files_by_tag)


class get_tags_by_file_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_get_tags_by_file(self):
        self.assertEquals(
            ['Tag B', 'Tag C', 'Tag D'], taggart.get_tags_by_file('file_3'))


class get_tags_by_file_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_get_tags_by_file(self):
        self.assertEquals(
            ['Tag B', 'Tag C', 'Tag D'], taggart.get_tags_by_file('file_3'))


class get_file_tags_alias_TestCase(BaseCase):
    def test_file_tags_alias(self):
        self.assertIs(taggart.get_file_tags, taggart.get_tags_by_file)


class get_tags_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_get_tags(self):
        self.assertEqual(
            ['Tag A', 'Tag B', 'Tag C', 'Tag D'], taggart.get_tags())


class get_tags_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_get_tags(self):
        self.assertEqual(
            ['Tag A', 'Tag B', 'Tag C', 'Tag D'], taggart.get_tags())


class get_files_TTF_TestCase(Taggart_TTF_BaseCase):
    def test_get_files(self):
        self.assertEqual(
            ['file_1', 'file_2', 'file_3'], taggart.get_files())


class get_files_FTT_TestCase(Taggart_FTT_BaseCase):
    def test_get_files(self):
        self.assertEqual(
            ['file_1', 'file_2', 'file_3'], taggart.get_files())
