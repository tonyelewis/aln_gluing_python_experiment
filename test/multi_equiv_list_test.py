# pytest-3 --verbose test

# Built-in
import os, sys

# PyPI
from pytest import raises

sys.path.append( os.path.join(os.path.dirname(__file__), '..' ) )

# To be tested
from cath.multi_equiv_list import _equiv_entry, get_alignment, multi_equiv_list, entry_res_id

def test_equiv_entry():
	assert( _equiv_entry(min=5,idx=5,max=5).min == 5 )
	assert( _equiv_entry(min=5,idx=5,max=5).idx == 5 )
	assert( _equiv_entry(min=5,idx=5,max=5).max == 5 )

	assert( _equiv_entry(min=4,idx=5,max=6).min == 4 )
	assert( _equiv_entry(min=4,idx=5,max=6).idx == 5 )
	assert( _equiv_entry(min=4,idx=5,max=6).max == 6 )

	with raises(Exception):
		_equiv_entry(min=6).idx = 5
	with raises(Exception):
		_equiv_entry(min=6).max = 5
	with raises(Exception):
		_equiv_entry(idx=5).min = 6
	with raises(Exception):
		_equiv_entry(idx=6).max = 5
	with raises(Exception):
		_equiv_entry(max=5).min = 6
	with raises(Exception):
		_equiv_entry(max=5).idx = 6

def test_equiv_entry_ordering():
	a_0 = _equiv_entry( idx=None )
	a_1 = _equiv_entry( idx=0    )
	a_2 = _equiv_entry( idx=1    )

	b_0 = _equiv_entry( idx=0    )
	b_1 = _equiv_entry( idx=1    )
	b_2 = _equiv_entry( idx=None )

	a  = [ a_0, a_1, a_2 ]
	b  = [ b_0, b_1, b_2 ]
	assert( not ( a_0 < b_0 ) )
	assert( not ( a_0 > b_0 ) )
	assert(       a_1 < b_1   )
	assert( not ( a_1 > b_1 ) )
	assert( not ( a_2 < b_2 ) )
	assert( not ( a_2 > b_2 ) )
	assert( a < b )

def test_constructor_works():
	assert( multi_equiv_list( 1       ).num_entries() == 1 )
	assert( multi_equiv_list( 1, 1    ).num_entries() == 2 )
	assert( multi_equiv_list( 1, 1, 1 ).num_entries() == 3 )
	with raises(Exception):
		multi_equiv_list()

def test_align_pair():
	meq = multi_equiv_list( 2, 3 )
	meq.link( entry_res_id( 0, 0 ), entry_res_id( 1, 0 ) )

	meq.link( entry_res_id( 0, 1 ), entry_res_id( 1, 2 ) )

	assert( get_alignment( meq ) == [
		(    0, 0 ),
		( None, 1 ),
		(    1, 2 ),
	] )

def test_align_triple():
	meq = multi_equiv_list( 3, 3, 3 )
	meq.link( entry_res_id( 0, 0 ), entry_res_id( 1, 0 ) )
	meq.link( entry_res_id( 0, 0 ), entry_res_id( 2, 0 ) )

	meq.link( entry_res_id( 2, 1 ), entry_res_id( 0, 1 ) )

	meq.link( entry_res_id( 1, 2 ), entry_res_id( 0, 2 ) )
	meq.link( entry_res_id( 2, 2 ), entry_res_id( 1, 2 ) )
	assert( get_alignment( meq ) == [
		(    0,    0,    0 ),
		(    1, None,    1 ),
		( None,    1, None ),
		(    2,    2,    2 ),
	] )

def test_align_join_joins():
	meq = multi_equiv_list( 1, 1, 1, 1 )
	meq.link( entry_res_id( 0, 0 ), entry_res_id( 1, 0 ) )
	meq.link( entry_res_id( 2, 0 ), entry_res_id( 3, 0 ) )
	meq.link( entry_res_id( 1, 0 ), entry_res_id( 2, 0 ) )

	assert( get_alignment( meq ) == [
		(    0,    0,    0,    0 ),
	] )

def test_rejects_joining_items_within_list():
	meq = multi_equiv_list( 3, 3, 3 )
	meq.link( entry_res_id( 0, 0 ), entry_res_id( 1, 0 ) )
	meq.link( entry_res_id( 1, 0 ), entry_res_id( 2, 0 ) )

	meq.link( entry_res_id( 0, 1 ), entry_res_id( 1, 1 ) )

	meq.link( entry_res_id( 1, 2 ), entry_res_id( 2, 2 ) )

	with raises(Exception):
		meq.link( entry_res_id( 0, 1 ), entry_res_id( 2, 2 ) )

def test_rejects_simple_cross():
	meq = multi_equiv_list( 2, 2, 2 )
	meq.link( entry_res_id( 0, 0 ), entry_res_id( 1, 1 ) )
	meq.link( entry_res_id( 1, 0 ), entry_res_id( 2, 1 ) )

	with raises(Exception):
		meq.link( entry_res_id( 0, 0 ), entry_res_id( 2, 0 ) )

def test_rejects_complex_cross():
	meq = multi_equiv_list( 1, 2, 2, 2 )
	meq.link( entry_res_id( 0, 0 ), entry_res_id( 1, 0 ) )

	meq.link( entry_res_id( 1, 1 ), entry_res_id( 2, 0 ) )

	meq.link( entry_res_id( 2, 1 ), entry_res_id( 3, 0 ) )
	with raises(Exception):
		meq.link( entry_res_id( 3, 1 ), entry_res_id( 0, 0 ) )
