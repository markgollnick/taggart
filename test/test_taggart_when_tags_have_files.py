import taggart
import unittest
from mock import Mock, call, patch


class Taggart_BaseCase(unittest.TestCase):

    def setUp(self):
        # Arrange
        reload(taggart)
        # Act
        taggart.tag('file_1.txt', 'Tag A')
        taggart.tag('file_2.txt', 'Tag B')
        taggart.tag('file_2.txt', 'Tag C')
        taggart.tag('file_3.txt', 'Tag B')
        taggart.tag('file_3.txt', 'Tag C')
        taggart.tag('file_3.txt', 'Tag D')
        self.addCleanup(patch.stopall)


class tag_TestCase(Taggart_BaseCase):

    def test_tag(self):
        # Arrange
        expect = {
            'Tag A': ['file_1.txt'],
            'Tag B': ['file_2.txt', 'file_3.txt'],
            'Tag C': ['file_2.txt', 'file_3.txt'],
            'Tag D': ['file_3.txt']
        }
        # Assert
        self.assertEqual(expect, taggart.THE_LIST)

    def test_tag_allows_existance_assertion(self):
        # Act/Assert
        self.assertRaises(
            IOError, taggart.tag, 'file.txt', 'New Tag', assert_exists=True)


class untag_TestCase(Taggart_BaseCase):

    def test_untag(self):
        # Arrange
        expect = {
            'Tag A': ['file_1.txt'],
            'Tag B': ['file_2.txt', 'file_3.txt'],
            'Tag C': ['file_2.txt'],
            'Tag D': ['file_3.txt']
        }
        # Act
        taggart.untag('file_3.txt', 'Tag C')
        taggart.untag('nonexistant.txt', 'No Problem')
        # Assert
        self.assertEqual(expect, taggart.THE_LIST)

    def test_untag_removes_empty_listings(self):
        # Arrange
        expect = {
            'Tag A': ['file_1.txt'],
            'Tag B': ['file_2.txt', 'file_3.txt'],
            'Tag C': ['file_2.txt', 'file_3.txt']
        }
        # Act
        taggart.untag('file_3.txt', 'Tag D')
        # Assert
        self.assertEqual(expect, taggart.THE_LIST)


class load_save_BaseCase(Taggart_BaseCase):

    def setUp(self):
        super(load_save_BaseCase, self).setUp()
        self.exists_mock = patch.object(taggart.os.path, 'exists').start()
        self.file_mock = Mock()
        real_open = __builtins__['open']
        self.open_mock = patch('__builtin__.open').start()
        self.open_mock.side_effect = lambda x, *args, **kwargs: (
            self.file_mock if x == 'mytags.txt'
            else real_open(x, *args, **kwargs))


class saved_TestCase(load_save_BaseCase):

    def _assert_save_success(self):
        self.exists_mock.assert_called_once_with('mytags.txt')
        self.open_mock.assert_called_once_with('mytags.txt', 'w')
        self.file_mock.write.assert_has_calls([
            call('Tag A<==>file_1.txt\n'),
            call('Tag B<==>file_2.txt\n'
                 'Tag B<==>file_3.txt\n'),
            call('Tag C<==>file_2.txt\n'
                 'Tag C<==>file_3.txt\n'),
            call('Tag D<==>file_3.txt\n')
        ])
        self.file_mock.close.assert_called_once_with()

    def test_save_case(self):
        # Arrange
        self.exists_mock.return_value = False
        # Act
        taggart.save('mytags.txt')
        # Assert
        self._assert_save_success()

    def test_save_disallows_overwrite_by_default(self):
        # Arrange
        self.exists_mock.return_value = True
        # Act/Assert
        self.assertRaises(IOError, taggart.save, 'mytags.txt')
        # Act
        taggart.save('mytags.txt', overwrite=True)
        # Assert
        self._assert_save_success()


class load_TestCase(load_save_BaseCase):

    def setUp(self):
        super(load_TestCase, self).setUp()

    def _assert_load_success(self):
        self.exists_mock.assert_called_once_with('mytags.txt')
        self.open_mock.assert_called_once_with('mytags.txt', 'r')
        self.file_mock.readlines.assert_called_once_with()
        self.file_mock.close.assert_called_once_with()
        expect = {
            'Tag A': ['file_1.txt'],
            'Tag B': ['file_2.txt', 'file_3.txt'],
            'Tag C': ['file_2.txt', 'file_3.txt'],
            'Tag D': ['file_3.txt']
        }
        self.assertEqual(expect, taggart.THE_LIST)

    def test_load(self):
        # Arrange
        reload(taggart)
        self.exists_mock.return_value = True
        self.file_mock.readlines.return_value = [
            'Tag A<==>file_1.txt\n',
            'Tag B<==>file_2.txt\n',
            'Tag B<==>file_3.txt\n',
            'Tag C<==>file_2.txt\n',
            'Tag C<==>file_3.txt\n',
            'Tag D<==>file_3.txt\n']
        # Act
        taggart.load('mytags.txt')
        # Assert
        self._assert_load_success()

    def test_load_overwrite_function_works(self):
        # Arrange
        reload(taggart)
        self.exists_mock.return_value = True
        self.file_mock.readlines.return_value = ['Tag Z<==>file_26.txt\n']
        expect = {
            'Tag A': ['file_1.txt'],
            'Tag Z': ['file_26.txt']
        }
        taggart.tag('file_1.txt', 'Tag A', assert_exists=False)
        # Act
        taggart.load('mytags.txt')
        # Assert
        self.assertEqual(expect, taggart.THE_LIST)
        # Arrange
        expect.pop('Tag A')
        # Act
        taggart.load('mytags.txt', overwrite=True)
        # Assert
        self.assertEqual(expect, taggart.THE_LIST)

    def test_load_fails_on_file_not_found(self):
        # Arrange
        self.exists_mock.return_value = False
        # Act/Assert
        self.assertRaises(IOError, taggart.load, 'mytags.txt')

    def test_load_allows_existence_assertion(self):
        # Arrange
        reload(taggart)
        self.exists_mock.side_effect = lambda x: (
            False if x == 'nonexistant.txt' else True)
        self.file_mock.readlines.return_value = [
            'Tag X<==>file_24.txt\n',
            'Tag Y<==>nonexistant.txt\n',
            'Tag Z<==>file_26.txt\n']
        # Act/Assert
        self.assertRaises(
            IOError, taggart.load, 'mytags.txt', assert_exists=True)


class rename_tag_TestCase(Taggart_BaseCase):

    def test_rename_tag(self):
        # Arrange
        expect = {
            'Tag Z': ['file_1.txt'],
            'Tag B': ['file_2.txt', 'file_3.txt'],
            'Tag C': ['file_2.txt', 'file_3.txt'],
            'Tag D': ['file_3.txt']
        }
        # Act
        taggart.rename_tag('Tag A', 'Tag Z')
        taggart.rename_tag('Some Nonexistant Tag, No Problem', 'Cool Tag')
        # Assert
        self.assertEqual(expect, taggart.THE_LIST)


class rename_file_TestCase(Taggart_BaseCase):

    def test_rename_file(self):
        # Arrange
        expect = {
            'Tag A': ['file_1.txt'],
            'Tag B': ['file_3.txt', 'renamed.txt'],
            'Tag C': ['file_3.txt', 'renamed.txt'],
            'Tag D': ['file_3.txt']
        }
        # Act
        taggart.rename_file('file_2.txt', 'renamed.txt')
        taggart.rename_file('some_nonexistant_file.txt', 'README.md')
        # Assert
        self.assertEqual(expect, taggart.THE_LIST)


class get_files_by_tag_TestCase(Taggart_BaseCase):

    def test_get_files_by_tag(self):
        # Arrange
        expects = [
            ['file_2.txt', 'file_3.txt'],
            ['file_3.txt']
        ]
        # Act
        result1 = taggart.get_files_by_tag('Tag C')
        result2 = taggart.get_files_by_tag('Tag D')
        # Assert
        self.assertEqual(expects[0], result1)
        self.assertEqual(expects[1], result2)


class get_tags_by_file_TestCase(Taggart_BaseCase):

    def test_get_tags_by_file(self):
        # Arrange
        expects = [
            ['Tag B', 'Tag C'],
            ['Tag B', 'Tag C', 'Tag D']
        ]
        # Act
        result1 = taggart.get_tags_by_file('file_2.txt')
        result2 = taggart.get_tags_by_file('file_3.txt')
        # Assert
        self.assertEqual(expects[0], result1)
        self.assertEqual(expects[1], result2)


class get_tags_TestCase(Taggart_BaseCase):

    def test_get_tags(self):
        self.assertEqual(
            ['Tag A', 'Tag B', 'Tag C', 'Tag D'],
            taggart.get_tags())


class get_files_TestCase(Taggart_BaseCase):

    def test_get_files(self):
        self.assertEqual(
            ['file_1.txt', 'file_2.txt', 'file_3.txt'],
            taggart.get_files())
