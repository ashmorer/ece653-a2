import unittest
from a2q3.verbal_arithmetic import solve

class PuzzleTests (unittest.TestCase):

    def setUp (self):
        """Reset Z3 context between tests"""
        import z3
        z3._main_ctx = None
    def tearDown (self):
        """Reset Z3 context after test"""
        import z3
        z3._main_ctx = None
        
    def test_1 (self):
        """SEND + MORE = MONEY"""
        res = solve ('SEND', 'MORE', 'MONEY')
        self.assertEquals (int(res[0])+int(res[1]), int(res[2]))

    def test_2 (self):
    	res = solve ('PLAY', 'THE', 'GAME')
        self.assertEquals (int(res[0])+int(res[1]), int(res[2]))

    def test_3 (self):
        res = solve ('ICE', 'CUBE', 'COOL')
        self.assertEquals (int(res[0])+int(res[1]), int(res[2]))

    
    def test_4 (self):
        res = solve ('SUN', 'TAN', 'BURN')
        self.assertEquals (int(res[0])+int(res[1]), int(res[2]))

    def test_5(self):
    	res = solve('ICE', 'CREAM', 'CONE')
    	self.assertEquals(res, None)
