import unittest
import server #create databases
from sqlalchemy import exc
import os
from functions import *
import authentication

class TestEnrol(unittest.TestCase):
    def setUp(self):
        server.createDatabases()

    def test_create_guest(self):
        before = len(loadAllGuestUsers())

        self.assertEqual(1, authentication.createGuestRequest('GUESTID', 'password', 'COMP1511, 17s2'))

        self.assertEqual(len(loadAllGuestUsers()), before + 1)

    def test_create_invalid_guest(self):
        before = len(loadAllGuestUsers())

        self.assertEqual(-1, authentication.createGuestRequest('', '', ''))

        self.assertEqual(len(loadAllGuestUsers()), before)


    def test_authenticate_guest(self):
        authentication.createGuestRequest('GUESTID2', 'password', 'COMP1511, 17s2')
        user = self.loadUser('GUESTID2')
        self.assertEqual('unassigned', user.role)

        toggleAuthenticationUser('GUESTID2')
        user = self.loadUser('GUESTID2')
        self.assertEqual('guest', user.role)

    def test_change_enrolment(self):
        authentication.createGuestRequest('GUESTID3', 'password', 'COMP1511, 17s2')
        user = self.loadUser('GUESTID3')
        self.assertEqual('COMP1511, 18s1' in user.courses, False)

        enrolUserToCourse('GUESTID3','COMP1511, 18s1')
        user = self.loadUser('GUESTID3')

        self.assertEqual('COMP1511, 18s1' in user.courses, True)

    def test_change_invalid_enrolment(self):
        authentication.createGuestRequest('GUESTID4', 'password', 'COMP1511, 17s2')
        user = self.loadUser('GUESTID4')
        before = len(user.courses)

        with self.assertRaises(ValueError):
            enrolUserToCourse('GUESTID4','')
        user = self.loadUser('GUESTID4')

        self.assertEqual(len(user.courses), before)


  

    def loadUser(self, userID):
        session = server.DBSession()

        user = session.query(User).filter(User.username==userID).first()
        session.close()
        return user

    def tearDown(self):
        os.remove('data.db')

if __name__ == "__main__":
    unittest.main()
