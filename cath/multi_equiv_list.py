from array       import array
from collections import namedtuple
from copy        import deepcopy
from functools   import total_ordering
from typing      import List, Tuple

entry_res_id = namedtuple( 'entry_res_id', [ 'entry', 'index' ] )

@total_ordering
class _equiv_entry:
	def __init__(self, *, idx: int = None, min: int = None, max: int = None):
		self._idx = None
		self._min = None
		self._max = None
		self.idx  = idx
		self.min  = min
		self.max  = max

	@property
	def idx(self):
		return self._idx

	@property
	def min(self):
		return self._min

	@property
	def max(self):
		return self._max

	@idx.setter
	def idx(self, value: int):
		if value is not None:
			if self.min is not None and value < self.min:
				raise Exception( "Cannot set _equiv_entry's idx to %d because min is %d" % ( value, self.min ) )
			if self.max is not None and value > self.max:
				raise Exception( "Cannot set _equiv_entry's idx to %d because max is %d" % ( value, self.max ) )
		# print( 'Setting idx to', value )
		self._idx = value

	@min.setter
	def min(self, value: int):
		if value is not None:
			if self.idx is not None and value > self.idx:
				raise Exception( "Cannot set _equiv_entry's min to %d because idx is %d" % ( value, self.idx ) )
			if self.max is not None and value > self.max:
				raise Exception( "Cannot set _equiv_entry's min to %d because max is %d" % ( value, self.max ) )
		# print( 'Setting min to', value )
		self._min = value

	@max.setter
	def max(self, value: int):
		if value is not None:
			if self.idx is not None and value < self.idx:
				raise Exception( "Cannot set _equiv_entry's max to %d because idx is %d" % ( value, self.idx ) )
			if self.min is not None and value < self.min:
				raise Exception( "Cannot set _equiv_entry's max to %d because min is %d" % ( value, self.min ) )
		# print( 'Setting max to', value )
		self._max = value

	def __repr__(self) -> str:
		return (
			  '_equiv_entry(idx='
			+ ( str( self.idx ) if self.idx is not None else 'None' )
			+ ', min='
			+ ( str( self.min ) if self.min is not None else 'None' )
			+ ', max='
			+ ( str( self.max ) if self.max is not None else 'None' )
			+ ')'
		)

	def __lt__(self, other):
		if other is not None:
			if self.idx is not None:
				if   other.min is not None and self.idx < other.min:
					return True
				elif other.idx is not None and self.idx < other.idx:
					return True
			elif self.max is not None:
				if   other.min is not None and self.max < other.min:
					return True
				elif other.idx is not None and self.max < other.idx:
					return True
		return False

	def __eq__(self, other):
		return not( self.__lt__( other ) ) and not( other.__lt__( self ) )

class multi_equiv_list:
	
	def __init__(self, *lengths: int):
		if not len( lengths ):
			raise Exception("Cannot build a multi_equiv_list with 0 entries")
		self.group_indices_by_entry = [ [ None ] * length for length in lengths ]
		self.groups = []

	def num_entries(self):
		return len( self.group_indices_by_entry )

	# def _get_direct_later_groups(self, group_idx: int) -> List[int]:
	# 	min_maxs_from_laters
	# 	max_mins_from_earliers
	# 	for ( entry, group_entry ) in enumerate( self.groups[ group_idx ] ):
	# 		if group_entry.idx is not None:

	# 		print(repr(group))
	# 		pass

	# def _get_all_later_groups(self, group_idx: int) -> List[int]:
	# 	return self._get_direct_later_groups(group_idx)

	def _join_groups(self, group_a_idx: int, group_b_idx: int) -> None:
		# TODO: Can this be better done with some sort of map
		new_group = []
		for entry, (group_a_entry, group_b_entry) in enumerate(zip(self.groups[group_a_idx],self.groups[group_b_idx])):
			if group_a_entry.idx is not None and group_b_entry.idx is not None:
				raise Exception("Cannot merge stuff")
			new_entry = _equiv_entry()
			new_entry.idx = group_a_entry.idx if group_a_entry.idx is not None else group_b_entry.idx
			new_entry.min = max( ( i for i in ( group_a_entry.min, group_b_entry.min ) if i is not None ), default=None )
			new_entry.max = min( ( i for i in ( group_a_entry.max, group_b_entry.max ) if i is not None ), default=None )
			new_group.append( new_entry )
			# if group_
			# print(repr({
			# 	'entry' : entry,
			# 	'group_a_entry' : group_a_entry,
			# 	'group_b_entry' : group_b_entry,
			# 	'new_entry' : new_entry,
			# }))
		# print(repr(new_group))
		self.groups[group_a_idx] = new_group
		for entry, group_b_entry in enumerate(self.groups[group_b_idx]):
			if group_b_entry.idx is not None:
				self.group_indices_by_entry[ entry ][group_b_entry.idx ] = group_a_idx
		self.groups[group_b_idx] = None

		return group_a_idx

	def _ensure_and_return_group_index(self, lhs: entry_res_id, rhs: entry_res_id):
		"""Ensure that there is a group for the two entry_res_ids and return it"""
		lhs_group_idx = self.group_indices_by_entry[ lhs.entry ][ lhs.index ]
		rhs_group_idx = self.group_indices_by_entry[ rhs.entry ][ rhs.index ]
		# If exactly one has a group index defined, return that one's group index
		if ( lhs_group_idx is None ) != ( rhs_group_idx is None ):
			return lhs_group_idx if lhs_group_idx is not None else rhs_group_idx
		
		# Else if neither have a group index, add a new group and return its index
		if ( lhs_group_idx is None and rhs_group_idx is None ):
			self.groups.append( [ _equiv_entry() for i in range( self.num_entries() ) ] )
			self.groups[ -1 ][ lhs.entry ].idx = lhs.index
			self.groups[ -1 ][ rhs.entry ].idx = rhs.index
			return len( self.groups ) - 1
		
		# Otherwise both have group indices
		# If those indices mismatch, raise an Exception (TODO: should attempt to join here)
		if lhs_group_idx != rhs_group_idx:
			return self._join_groups( lhs_group_idx, rhs_group_idx )

		# Otherwise return the group index both share
		return lhs_group_idx

	# def _ensure_set_and_return_group_index(self, lhs: entry_res_id, rhs: entry_res_id):
	# 	"""Ensure that there is a group for the two entry_res_ids,
	# 	which they're both pointing to, and return it"""

	# 	# Ensure there's a group ID, set both to point to it and return it
	# 	group_id = self._ensure_and_return_group_index( lhs, rhs )
	# 	self.group_indices_by_entry[ lhs.entry ][ lhs.index ] = group_id
	# 	self.group_indices_by_entry[ rhs.entry ][ rhs.index ] = group_id
	# 	return group_id
	def do_link(self, lhs: entry_res_id, rhs: entry_res_id) -> None:
		# Ensure there's a group ID, set both to point to it and return it
		group_id = self._ensure_and_return_group_index( lhs, rhs )
		self.groups[group_id][lhs.entry].idx = lhs.index
		self.groups[group_id][rhs.entry].idx = rhs.index
		self.group_indices_by_entry[ lhs.entry ][ lhs.index ] = group_id
		self.group_indices_by_entry[ rhs.entry ][ rhs.index ] = group_id
		# self._get_all_later_groups( group_id )

	def link(self, lhs: entry_res_id, rhs: entry_res_id) -> None:
		# group_id = self._ensure_and_return_group_index( lhs, rhs )
		# self.groups[group_id][lhs.entry].idx = lhs.index
		# self.groups[group_id][rhs.entry].idx = rhs.index
		# self.group_indices_by_entry[ lhs.entry ][ lhs.index ] = group_id
		# self.group_indices_by_entry[ rhs.entry ][ rhs.index ] = group_id
		copy_of_self = deepcopy( self )
		copy_of_self.do_link( lhs, rhs )
		get_psuedo_alignment( copy_of_self )
		self.do_link( lhs, rhs )

def get_psuedo_alignment(meq: multi_equiv_list):
	sorted_groups = sorted( [ i for i in meq.groups if i is not None ] )
	result = []
	if len( sorted_groups ):
		group_len = len( sorted_groups[ 0 ] )
		up_to = array( 'l', [ -1, ] * group_len )
		for group in sorted_groups:
			for entry, group_val in enumerate( group ):
				if group_val.idx is not None:
					if up_to[ entry ] + 1 > group_val.idx:
						raise Exception(
							  "Ohh nooo, entry: "
							+ str( entry )
							+ ", expected index to be at "
							+ str( up_to[ entry ] + 1 )
							+ " but index in group is only "
							+ str( group_val.idx )
							+ " perhaps because of some sort of invalid cross"
						)
					while up_to[ entry ] + 1 < group_val.idx:
						(up_to[ entry ]) += 1
						new_row = [ None, ] * group_len
						new_row[ entry ] = up_to[ entry ]
						result.append( tuple( new_row ) )
					(up_to[ entry ]) += 1
			result.append( tuple( group_val.idx for group_val in group ) )

	return result


