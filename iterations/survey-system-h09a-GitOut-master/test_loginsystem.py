import unittest
import server #create databases
from sqlalchemy import exc
import os
from functions import *
from authentication import *
import time

class TestLoginSystem(unittest.TestCase):
    def setUp(self):
        server.createDatabases()

    def test_admin_login(self):
        user = login('1', 'password')
        self.assertNotEqual(user, -1)
        self.assertNotEqual(user, 0)
        self.assertNotEqual(user, None)

        self.assertEqual(user.role, 'admin')

        logout()

    def test_staff_login(self):
        user = login('50', 'staff670')
        self.assertNotEqual(user, -1)
        self.assertNotEqual(user, 0)
        self.assertNotEqual(user, None)

        self.assertEqual(user.role, 'staff')

        logout()

    def test_student_login(self):
        user = login('100', 'student228')
        self.assertNotEqual(user, -1)
        self.assertNotEqual(user, 0)
        self.assertNotEqual(user, None)

        self.assertEqual(user.role, 'student')

        logout()

    def test_enrolled_guest_login(self):
        createGuestRequest('GUESTID1', 'password', 'COMP1511, 17s2')
        user = login('GUESTID1', 'password')
        if(user == 0):
            toggleAuthenticationUser('GUESTID1')

        user = login('GUESTID1', 'password')

        self.assertNotEqual(user, -1)
        self.assertNotEqual(user, 0)
        self.assertNotEqual(user, None)

        self.assertEqual(user.role, 'guest')

        logout()

    def test_incorrect_login(self):
        user = login('wrongusername', 'student228')
        self.assertEqual(user, -1)

    def test_incorrect_password(self):
        user = login('100', 'wrongpassword')
        self.assertEqual(user, -1)

    def test_unassigned_guest_login(self):
        createGuestRequest('GUESTID2', 'password', 'COMP1511, 17s2')
        user = login('GUESTID2', 'password')

        self.assertEqual(user, -0)


    def loadUser(self, userID):
        session = server.DBSession()

        user = session.query(User).filter(User.username==userID).first()
        session.close()
        return user

    def tearDown(self):
        os.remove("data.db")

if __name__ == "__main__":
    unittest.main()
    

