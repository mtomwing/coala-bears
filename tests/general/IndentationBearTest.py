import unittest
from queue import Queue

from bears.general.IndentationBear import IndentationBear
from bears.general.AnnotationBear import AnnotationBear
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting


class IndentationBearTest(unittest.TestCase):

    def setUp(self):
        self.section = Section("")
        self.section.append(Setting('language', 'c'))
        self.section.append(Setting('language_family', 'c'))
        self.section.append(Setting('use_spaces', False))
        self.dep_uut = AnnotationBear(self.section, Queue())

    def get_results(self, file, section=None):
        if section is None:
            section = self.section
        dep_results_valid = self.dep_uut.execute("file", file)
        uut = IndentationBear(section, Queue())
        arg_dict = {'dependency_results':
                    {AnnotationBear.__name__:
                     list(dep_results_valid)},
                    'file': file}
        return list(uut.run_bear_from_section(["file"], arg_dict))

    def verify_bear(self,
                    valid_file=None,
                    invalid_file=None,
                    section=None):
        if valid_file:
            valid_results = self.get_results(valid_file, section)
            self.assertEqual(valid_results, [])

        if invalid_file:
            invalid_results = self.get_results(invalid_file, section)
            self.assertNotEqual(invalid_results, [])

    def test_basic_indent(self):
        valid_file =\
            ("{\n",
             "\tright indent\n",
             "}\n")
        invalid_file =\
            ("{\n",
             "wrong indent\n",
             "}\n")
        self.verify_bear(valid_file, invalid_file)

        valid_file2 =\
            ("a {\n",
             "\tindent1\n",
             "\tindent2\n",
             "}\n")

        invalid_file2 =\
            ("a {\n",
             "\tindentlevel1;\n",
             "\t\tsecondlinehere;\n",
             "}\n")
        self.verify_bear(valid_file2, invalid_file2)

    def test_within_strings(self):
        valid_file1 =\
            ('"indent withinstring{"\n',
             'No indent\n')
        self.verify_bear(valid_file1)

        valid_file2 =\
            ('R("strings can span\n',
             'multiple lines as well{")\n'
             'but the bear works correctly\n')
        self.verify_bear(valid_file2)

        valid_file3 =\
            ('"this should indent"{ "hopefully"\n',
             '\tand it does\n',
             '}\n')
        self.verify_bear(valid_file3)

    def test_within_comments(self):
        valid_file1 =\
            ('//indent within comments{\n',
             'remains unindented\n')
        self.verify_bear(valid_file1)

        valid_file2 =\
            ('/*Indent within\n',
             'lines of multiline comment {\n',
             'doesnt have any effect{ */\n',
             'no affect on regular lines as well\n')
        self.verify_bear(valid_file2)

        valid_file3 =\
            ('/*this should indent*/{ /*hopefully*/\n',
             '\tand it does\n',
             '}\n')
        self.verify_bear(valid_file3)

    def test_branch_indents(self):
        valid_file =\
            ('branch indents{\n',
             '\tsecond branch{\n',
             '\t\twithin second branch\n',
             '\t}\n',
             '}\n',)
        self.verify_bear(valid_file)

    def test_bracket_matching(self):
        valid_file = ("{{{}{}}",
                      "\tone_indent",
                      "}")
        invalid_file = ("{{{}{}}",
                        "didn't give indent",
                        "}")
        self.verify_bear(valid_file, invalid_file)

    def test_blank_lines(self):
        valid_file = ("{ trying indent",
                      "    ",
                      "\tIndents even after blank line}")
        invalid_file = ("{ trying indent",
                        "    ",
                        "should've Indented after blank line}")
        self.verify_bear(valid_file, invalid_file)

    def test_settings(self):
        section = Section("")
        section.append(Setting('language', 'c'))
        section.append(Setting('language_family', 'c'))
        section.append(Setting('use_spaces', True))
        section.append(Setting('tab_width', 6))
        valid_file = ('{\n',
                      # Start ignoring SpaceConsistencyBear
                      '      6 spaces of indentation\n'
                      # Stop ignoring
                      '}\n')

        invalid_file = ('{\n',
                        # Start ignoring SpaceConsistencyBearW
                        '    4 spaces of indentation\n'
                        # Stop ignoring
                        '}\n')
        self.verify_bear(valid_file, invalid_file, section)

    def test_unmatched_indents(self):
        valid_file = ('{}\n',)
        invalid_file = ('{\n',)
        self.verify_bear(valid_file, invalid_file)

        invalid_file2 = ('{}}\n',)
        self.verify_bear(valid_file=None, invalid_file=invalid_file2)
