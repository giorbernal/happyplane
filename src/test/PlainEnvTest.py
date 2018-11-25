# PlainEnvironment module test

import unittest
import sys

sys.path.append('../main')

from PlaneEnvironment import PlaneEnv

class PlainEnvTest(unittest.TestCase):

	def testActionSample(self):
		env = PlaneEnv('../../planes/plane1.txt')
		action = env.action_space_sample()
		self.assertTrue(action in [0,1,2,3,4],'Action ' + str(action) + ' is not one of this 0,1,2,3,4')

	def testStatus(self):
		env = PlaneEnv('../../planes/plane1.txt')
		for g in env.Groups:
			for p in g:
				if (p.id=='1w'):
					self.assertEqual(p.status,1)
				else:
					self.assertEqual(p.status,0)

	def testNextPassenger(self):
		env = PlaneEnv('../../planes/plane1.txt')
		passengers = env.passengerList
		self.assertEqual(passengers.getNext().id,'1w')

	def testRotate(self):
		env = PlaneEnv('../../planes/plane1.txt')
		passengers = env.passengerList
		canRotate = passengers.canRotate()
		self.assertFalse(canRotate, 'It should not rotate')

	def testReadAll(self):
		env = PlaneEnv('../../planes/plane1.txt')
		passengers = env.passengerList
		while (passengers.completed==False):
			id=passengers.getNextAndUpdate().id
		self.assertTrue(passengers.getNext() is None)

#    def test_split(self):
#        s = 'hello world'
#        self.assertEqual(s.split(), ['hello', 'world'])
#        # check that s.split fails when the separator is not a string
#        with self.assertRaises(TypeError):
#            s.split(2)

if __name__ == '__main__':
    unittest.main()