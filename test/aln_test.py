# pytest-3 --verbose test

# Built-in
import os, sys

# PyPI
from pytest import raises

sys.path.append( os.path.join(os.path.dirname(__file__), '..' ) )

# To be tested
from cath.multi_aln import combine_scores, ScoreComboMethod

def test_combine_scores_works_on_9_and_25():
	assert( combine_scores( ScoreComboMethod.GEOM_MEAN, 9, 25 ) == 15 )
	assert( combine_scores( ScoreComboMethod.MAX,       9, 25 ) == 25 )
	assert( combine_scores( ScoreComboMethod.MIN,       9, 25 ) ==  9 )


def test_returns_none_if_none_in_input():
	assert( combine_scores( ScoreComboMethod.GEOM_MEAN, 9, None, 25 ) == None )
	assert( combine_scores( ScoreComboMethod.MAX,       9, None, 25 ) == None )
	assert( combine_scores( ScoreComboMethod.MIN,       9, None, 25 ) == None )

def test_raises_on_empty_array():
	with raises(Exception):
		combine_scores( ScoreComboMethod.GEOM_MEAN )
	with raises(Exception):
		combine_scores( ScoreComboMethod.MAX       )
	with raises(Exception):
		combine_scores( ScoreComboMethod.MIN       )
