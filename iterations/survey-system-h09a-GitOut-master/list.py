"""
File: list.py
Date: 12 October 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: This file contains the functions for being able to
			 store lists in sql by converting them into json strings.
"""

# Imported libraries...
from sqlalchemy.types import TypeDecorator, String
import json

# This class stores the ability to store lists in SQL by converting them to json strings.
class Json(TypeDecorator):
	impl = String

	def process_bind_param(self, value, dialect):
		return json.dumps(value)

	def process_result_value(self, value, dialect):
		return json.loads(value)
