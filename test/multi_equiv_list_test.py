# pytest-3 --verbose test

# Built-in
import os, sys

# PyPI
from pytest import raises

sys.path.append( os.path.join(os.path.dirname(__file__), '..' ) )

# To be tested
from cath.multi_equiv_list import multi_equiv_list

def test_constructor_works():
	assert( multi_equiv_list( 1 ).num_entries() == 1 )
	assert( multi_equiv_list( 2 ).num_entries() == 2 )
	assert( multi_equiv_list( 3 ).num_entries() == 3 )
	with raises(Exception):
		multi_equiv_list( 0 )
