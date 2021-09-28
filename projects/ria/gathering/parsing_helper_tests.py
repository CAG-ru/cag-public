#!/usr/bin/env python3
import unittest

from parsing_helper import split_value


class TestSplitValues(unittest.TestCase):
    """Тестирование функции split_values в parsing_helper"""

    @classmethod
    def setUpClass(cls):
        """Set up for class"""
        print("setUpClass")
        print("==========")

    @classmethod
    def tearDownClass(cls):
        """Tear down for class"""
        print("==========")
        print("tearDownClass")

    def setUp(self):
        """Set up for test"""
        print("Set up for [" + self.shortDescription() + "]")

    def tearDown(self):
        """Tear down for test"""
        print("Tear down for [" + self.shortDescription() + "]")
        print('')

    def test_starts_with_newline(self):
        """Случай, когда первая строка осталась пустая"""
        # Пример: отчёт 113030 (секция 5)
        text = "\r\nСобственно, текст"
        sv = split_value(text)
        self.assertEqual(len(sv), 1)

    def test_starts_with_enumeration_and_dot(self):
        """Случай с нумерованным списком и точкой"""
        # Пример: отчёт 98518 (секция 5)
        text = "1. пункт 1;" \
               "\r\n2. пункт 2."
        sv = split_value(text)
        self.assertEqual(len(sv), 2)

    def test_starts_with_enumeration_and_round_bracket(self):
        """Случай с нумерованным списком и закрывающей скобкой"""
        text = "1) пункт 1;" \
               "\r\n2) пункт 2."
        sv = split_value(text)
        self.assertEqual(len(sv), 2)

    def test_starts_with_hyphen(self):
        """Случай с маркером-дефисом"""
        text = "- пункт 1;" \
               "\r\n- пункт 2."
        sv = split_value(text)
        self.assertEqual(len(sv), 2)

    def test_starts_with_letter(self):
        """Случай с маркером-буквой"""
        # Пример: 44976 (секция 5)
        text = "а) пункт 1; \n" \
               "б) пункт 2."
        sv = split_value(text)
        self.assertEqual(len(sv), 2)

    def test_starts_with_bullet(self):
        """Случай с маркером-точкой"""
        # Пример: 93125 (секция 5)
        text = "• пункт 1;\n" \
               "• пункт 2."
        sv = split_value(text)
        self.assertEqual(len(sv), 2)

    def test_has_title(self):
        """Случай с заголовком"""
        # Пример: 83355 (секция 5)
        text = "Заголовок:\n" \
               "- пункт 1;\n" \
               "- пункт 2."
        sv = split_value(text)
        self.assertEqual(len(sv), 3)  # Хотим заголовок как отдельную строчку

    def test_has_title_within_paragraph(self):
        """Случай со вложенным заголовком между пунктами"""
        # Пример:
        # TODO
        pass

    def test_markers_without_newline_character(self):
        """Случай, когда перед маркерами нет знака перевода строки"""
        # Пример, отчёт 100697 (секция 5)
        text = " 1. Пункт раз. 2. Пункт дваз. 3. Пункт триз."
        sv = split_value(text)
        self.assertEqual(len(sv), 1)

    def test_markers_and_newline_within_items(self):
        """Случай, когда есть маркеры и перевод строки внутри пункта"""
        # Пример, отчёт 47498 (секция 4)
        text = " 1. Пункт раз. 2. Пункт\n дваз."
        sv = split_value(text)
        self.assertEqual(len(sv), 2)

    def test_no_markers_and_newline_between_items(self):
        """Случай, когда нет маркеров и есть перевод строки внутри пункта"""
        # Пример, отчёт 47498 (секция 4)
        text = "Первый\r\nВторой\r\nТретий"
        sv = split_value(text)
        self.assertEqual(len(sv), 3)


if __name__ == '__main__':
    unittest.main()
