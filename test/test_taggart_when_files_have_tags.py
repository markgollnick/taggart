import taggart
import unittest
from mock import Mock, call, patch


class Taggart_BaseCase(unittest.TestCase):

    def setUp(self):
        # Arrange
        reload(taggart)
        taggart.FORMAT = taggart.FILE_TO_TAG
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
            'file_1.txt': ['Tag A'],
            'file_2.txt': ['Tag B', 'Tag C'],
            'file_3.txt': ['Tag B', 'Tag C', 'Tag D']
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
            'file_1.txt': ['Tag A'],
            'file_2.txt': ['Tag B', 'Tag C'],
            'file_3.txt': ['Tag D', 'Tag B']
        }
        # Act
        taggart.untag('file_3.txt', 'Tag C')
        taggart.untag('nonexistant.txt', 'No Problem')
        # Assert
        self.assertEqual(expect, taggart.THE_LIST)

    def test_untag_removes_empty_listings(self):
        # Arrange
        expect = {
            'file_2.txt': ['Tag B', 'Tag C'],
            'file_3.txt': ['Tag B', 'Tag C', 'Tag D']
        }
        # Act
        taggart.untag('file_1.txt', 'Tag A')
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
            call('file_1.txt<==>Tag A\n'),
            call('file_2.txt<==>Tag B\n'
                 'file_2.txt<==>Tag C\n'),
            call('file_3.txt<==>Tag B\n'
                 'file_3.txt<==>Tag C\n'
                 'file_3.txt<==>Tag D\n')
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
            'file_1.txt': ['Tag A'],
            'file_2.txt': ['Tag B', 'Tag C'],
            'file_3.txt': ['Tag B', 'Tag C', 'Tag D']
        }
        self.assertEqual(expect, taggart.THE_LIST)

    def test_load(self):
        # Arrange
        reload(taggart)
        taggart.FORMAT = taggart.FILE_TO_TAG
        self.exists_mock.return_value = True
        self.file_mock.readlines.return_value = [
            'file_1.txt<==>Tag A\n',
            'file_2.txt<==>Tag B\n',
            'file_2.txt<==>Tag C\n',
            'file_3.txt<==>Tag B\n',
            'file_3.txt<==>Tag C\n',
            'file_3.txt<==>Tag D\n']
        # Act
        taggart.load('mytags.txt')
        # Assert
        self._assert_load_success()

    def test_load_overwrite_function_works(self):
        # Arrange
        reload(taggart)
        taggart.FORMAT = taggart.FILE_TO_TAG
        self.exists_mock.return_value = True
        self.file_mock.readlines.return_value = ['file_26.txt<==>Tag Z\n']
        expect = {
            'file_1.txt': ['Tag A'],
            'file_26.txt': ['Tag Z']
        }
        taggart.tag('file_1.txt', 'Tag A', assert_exists=False)
        # Act
        taggart.load('mytags.txt')
        # Assert
        self.assertEqual(expect, taggart.THE_LIST)
        # Arrange
        expect.pop('file_1.txt')
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
        taggart.FORMAT = taggart.FILE_TO_TAG
        self.exists_mock.side_effect = lambda x: (
            False if x == 'nonexistant.txt' else True)
        self.file_mock.readlines.return_value = [
            'file_24.txt<==>Tag X\n',
            'nonexistant.txt<==>Tag Y\n',
            'file_26.txt<==>Tag Z\n']
        # Act/Assert
        self.assertRaises(
            IOError, taggart.load, 'mytags.txt', assert_exists=True)


class rename_tag_TestCase(Taggart_BaseCase):

    def test_rename_tag(self):
        # Arrange
        expect = {
            'file_1.txt': ['Tag Z'],
            'file_2.txt': ['Tag B', 'Tag C'],
            'file_3.txt': ['Tag B', 'Tag C', 'Tag D']
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
            'file_1.txt': ['Tag A'],
            'renamed.txt': ['Tag B', 'Tag C'],
            'file_3.txt': ['Tag B', 'Tag C', 'Tag D']
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
