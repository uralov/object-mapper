# coding=utf-8
"""
Copyright (C) 2015, marazt. All rights reserved.
"""
import unittest

from datetime import datetime
from mapper.object_mapper import ObjectMapper
from mapper.object_mapper_exception import ObjectMapperException


class ToTestClass(object):
    """ To Test Class """
    def __init__(self):
        self.name = ""
        self.date = ""
        pass


class ToTestClassTwo(object):
    """ To Test Class Two """
    def __init__(self):
        self.all = ""
        pass


class ToTestClassEmpty(object):
    """ To Test Class Empty """
    def __init__(self):
        pass


class FromTestClass(object):
    """ From Test Class """
    def __init__(self):
        self.name = "Igor"
        self.surname = "Hnizdo"
        self.date = datetime(2015, 1, 1)
        pass


class ObjectMapperTest(unittest.TestCase):
    """
    Unit tests for the `ObjectMapper` module.
    """

    def test_mapping_creation_without_mappings_correct(self):
        """ Test mapping creation without mappings """

        # Arrange
        from_class = FromTestClass()
        mapper = ObjectMapper()
        mapper.create_map(FromTestClass, ToTestClass)

        # Act
        result = mapper.map(FromTestClass(), ToTestClass)

        # Assert
        self.assertTrue(isinstance(result, ToTestClass), "Target types must be same")
        self.assertEqual(result.name, from_class.name, "Name mapping must be equal")
        self.assertEqual(result.date, from_class.date, "Date mapping must be equal")
        self.assertNotIn("surname", result.__dict__, "To class must not contain surname")

    def test_mapping_creation_with_mappings_correct(self):
        """ Test mapping creation with mappings """

        # Arrange
        from_class = FromTestClass()
        mapper = ObjectMapper()
        mapper.create_map(FromTestClass, ToTestClass,
                          {"name": lambda x: "{0} {1}".format(x.name, x.surname),
                           "date": lambda x: "{0} Hi!".format(str(x.date))})
        mapper.create_map(FromTestClass, ToTestClassTwo,
                          {"all": lambda x: "{0}{1}{2}".format(x.name, x.surname, x.date)})
        mapper.create_map(ToTestClassTwo, ToTestClassEmpty)

        # Act
        result1 = mapper.map(from_class, ToTestClass)
        result2 = mapper.map(from_class, ToTestClassTwo)
        result3 = mapper.map(result2, ToTestClassEmpty)

        # Assert
        self.assertTrue(isinstance(result1, ToTestClass), "Type must be ToTestClass")
        self.assertEqual(result1.name, "{0} {1}".format(from_class.name, from_class.surname),
                         "Name mapping must be equal")
        self.assertEqual(result1.date, "{0} Hi!".format(from_class.date), "Date mapping must be equal")
        self.assertNotIn("surname", result1.__dict__, "To class must not contain surname")

        self.assertTrue(isinstance(result2, ToTestClassTwo), "Type must be ToTestClassTwo")
        self.assertEqual(result2.all,
                         "{0}{1}{2}".format(from_class.name, from_class.surname, from_class.date),
                         "There must be concatenated all properties of fromTestClass")
        self.assertNotIn("name", result2.__dict__, "To class must not contain name")
        self.assertNotIn("surname", result2.__dict__, "To class must not contain surname")
        self.assertNotIn("date", result2.__dict__, "To class must not contain date")

        self.assertTrue(isinstance(result3, ToTestClassEmpty), "Type must be ToTestClassEmpty")
        self.assertTrue(len(result3.__dict__) == 0, "There must be no attributes")

    def test_mapping_creation_duplicate_mapping(self):
        """ Test mapping creation with duplicate mappings """

        # Arrange
        exc = False
        msg = "Mapping for FromTestClass -> ToTestClass already exists"
        mapper = ObjectMapper()

        mapper.create_map(FromTestClass, ToTestClass)

        # Act
        try:
            mapper.create_map(FromTestClass, ToTestClass, {})
        except ObjectMapperException as ex:
            self.assertEqual(str(ex), msg, "Exception message must be correct")
            exc = True

        # Assert
        self.assertTrue(exc, "Exception must be thrown")

    def test_mapping_creation_invalid_mapping_function(self):
        """ Test mapping creation with invalid mapping function """

        # Arrange
        exc = False
        msg = "Invalid mapping function while setting property ToTestClass.date"
        mapper = ObjectMapper()
        mapper.create_map(FromTestClass, ToTestClass, {"date": lambda x: x.be + x.de})

        # Act
        try:
            mapper.map(FromTestClass(), ToTestClass)
        except ObjectMapperException as ex:
            self.assertEqual(str(ex), msg, "Exception message must be correct")
            exc = True

        # Assert
        self.assertTrue(exc, "Exception must be thrown")

    def test_mapping_creation_none_target(self):
        """ Test mapping creation with none target """

        # Arrange
        exc = None
        from_class = None
        mappings = \
            {
                "name": lambda x: x.name + " " + x.surname,
                "date": lambda x: str(x.date) + " Happy new year!"
            }

        mapper = ObjectMapper()
        mapper.create_map(FromTestClass, ToTestClass, mappings)

        # Act
        try:
            mapper.map(from_class, ToTestClass)
        except AttributeError as ex:
            exc = ex

        # Assert
        self.assertIsNotNone(exc, "AttributeError must be thrown")
        self.assertEqual("'NoneType' object has no attribute '__dict__'", str(exc))

    def test_mapping_with_none_source_and_allow_none_returns_none(self):
        """ Test mapping with none source and allow none returns none """

        # Arrange
        from_class = None
        mappings = \
            {
                "name": lambda x: x.name + " " + x.surname,
                "date": lambda x: str(x.date) + " Happy new year!"
            }

        mapper = ObjectMapper()
        mapper.create_map(FromTestClass, ToTestClass, mappings)

        # Act
        result = mapper.map(from_class, ToTestClass, allow_none=True)

        # Assert
        self.assertEqual(None, result)

    def test_mapping_creation_no_mapping_defined(self):
        """ Test mapping creation with no mapping defined """

        # Arrange
        exc = False
        msg = "No mapping defined for FromTestClass -> ToTestClass"
        from_class = FromTestClass()

        mapper = ObjectMapper()

        # Act
        try:
            mapper.map(from_class, ToTestClass)
        except ObjectMapperException as ex:
            self.assertEqual(str(ex), msg, "Exception message must be correct")
            exc = True

        # Assert
        self.assertTrue(exc, "Exception must be thrown")

    def test_mapping_creation_with_mapping_suppression(self):
        """ Test mapping creation with mapping suppression """

        # Arrange
        from_class = FromTestClass()
        mapper = ObjectMapper()
        mapper.create_map(FromTestClass, ToTestClass,
                          {"name": None})

        # Act
        result1 = mapper.map(from_class, ToTestClass)

        # Assert
        self.assertTrue(isinstance(result1, ToTestClass), "Type must be ToTestClass")
        self.assertEqual(result1.name, "", "Name must not be mapped")
        self.assertEqual(result1.date, from_class.date, "Date is set by property name")
        self.assertNotIn("surname", result1.__dict__, "To class must not contain surname")

    def test_mapping_with_case_insensitivity(self):
        """ Test mapping with case insensitivity """

        # Arrange
        class ToTestClass2(object):
            """ To Test Class 2 """
            def __init__(self):
                self.name = ""

        class FromTestClass2(object):
            """ From Test Class 2 """
            def __init__(self):
                self.Name = "Name"

        from_class = FromTestClass2()
        mapper = ObjectMapper()
        mapper.create_map(FromTestClass2, ToTestClass2)

        # Act
        result = mapper.map(FromTestClass2(), ToTestClass2, ignore_case=True)

        # Assert
        self.assertEqual(result.name, from_class.Name, "Name mapping must be equal")

    def test_mapping_creation_with_partial_mapping_correct(self):
        """ Test mapping creation with partial mapping """

        # Arrange
        from_class = FromTestClass()
        mapper = ObjectMapper()
        mapper.create_map(FromTestClass, ToTestClass,
                          {"name": lambda x: "{0} {1}".format(x.name, x.surname)})

        # Act
        result1 = mapper.map(from_class, ToTestClass)

        # Assert
        self.assertTrue(isinstance(result1, ToTestClass), "Type must be ToTestClass")
        self.assertEqual(result1.name, "{0} {1}".format(from_class.name, from_class.surname),
                         "Name mapping must be equal")
        self.assertEqual(result1.date, from_class.date, "Date mapping must be equal")
        self.assertNotIn("surname", result1.__dict__, "To class must not contain surname")

    def test_mapping_creation_with_custom_dir(self):
        """ Test mapping to objects with custom __dir__ behaviour """

        # Arrange
        _propNames = ['name', 'date']
        class ToCustomDirClass(object):
            def __dir__(self):
                props = list(self.__dict__.keys())
                props.extend(_propNames)
                return props

            def __init__(self):
                self.props = {k: None for k in _propNames}

            def __getattribute__(self, name):
                if name in _propNames:
                    return self.props[name]
                else:
                    return object.__getattribute__(self, name)

            def __setattr__(self, name, value):
                if name in _propNames:
                    self.props[name] = value
                else:
                    return object.__setattr__(self, name, value)

        # Arrange
        from_class = FromTestClass()
        mapper = ObjectMapper()
        mapper.create_map(FromTestClass, ToCustomDirClass)

        # Act
        result = mapper.map(FromTestClass(), ToCustomDirClass)

        # Assert
        self.assertTrue(isinstance(result, ToCustomDirClass), "Target types must be same")
        self.assertEqual(result.name, from_class.name, "Name mapping must be equal")
        self.assertEqual(result.date, from_class.date, "Date mapping must be equal")
        self.assertNotIn("surname", dir(result), "To class must not contain surname")