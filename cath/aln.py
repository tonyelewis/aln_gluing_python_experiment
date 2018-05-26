from collections import namedtuple
from copy        import deepcopy
from typing      import List

from .pdb_sequence import pdb_residue, pdb_sequence

ssap_aln_entry = namedtuple('ssap_aln_entry', [ 'left_residue', 'right_residue', 'score' ])

class alignment:
	
	def __init__(self, num_entries):
		self.scores                       = [] # type: List
		self.equiv_rows                   = [] # type: List
		self.aln_index_by_index_per_entry = [] # type: List
		for dummy in range( num_entries ):
			self.aln_index_by_index_per_entry.append( [] )

	def num_entries(self):
		return len( self.aln_index_by_index_per_entry )

	def length(self):
		return len( self.equiv_rows )

	def append(self, equivs, score):
		if len( equivs ) != self.num_entries():
			raise Exception("Cannot add row with " + str( len( equivs ) ) + " entries to alignment with " + str( self.num_entries() ) + " entries")
		
		for ( aln_index_by_index, new_equiv ) in zip( self.aln_index_by_index_per_entry, equivs ):
			if new_equiv != None:
				if ( new_equiv != len( aln_index_by_index ) ):
					raise Exception("Argh")
				aln_index_by_index.append( self.length() )

		self.equiv_rows.append(equivs)
		self.scores.append(score)

	def flip(self):
		if self.num_entries() != 2:
			raise Exception("Can only flip pairwise alignment")
		self.aln_index_by_index_per_entry.reverse()
		for equiv_row in self.equiv_rows:
			equiv_row.reverse()

	def __str__(self):
		return                                    'alignment[\n\tscores:'              + repr(
			self.scores                       ) + ',\n\tequiv_rows:'                   + repr(
			self.equiv_rows                   ) + ',\n\taln_index_by_index_per_entry:' + repr(
			self.aln_index_by_index_per_entry ) + '\n]'

def flip_copy(alignment: alignment) -> alignment:
	new_aln = deepcopy( alignment )
	new_aln.flip()
	return new_aln

def ssap_aln_line_empty_parts():
	return [ '0', '0', '0', '0' ]

def left_is_present(ssap_aln_line_parts):
	return ssap_aln_line_parts[ :4 ] != ssap_aln_line_empty_parts()

def right_is_present(ssap_aln_line_parts):
	return ssap_aln_line_parts[ 5: ] != ssap_aln_line_empty_parts()

def get_left_residue(ssap_aln_line_parts):
	return pdb_residue(
		pdb_residue_number = int( ssap_aln_line_parts[ 0 ] ),
		pdb_insert_code    = int( ssap_aln_line_parts[ 2 ] ) or None,
		amino_acid         =      ssap_aln_line_parts[ 3 ],
	 ) if left_is_present( ssap_aln_line_parts ) else None

def get_right_residue(ssap_aln_line_parts):
	return pdb_residue(
		pdb_residue_number = int( ssap_aln_line_parts[ 8 ] ),
		pdb_insert_code    = int( ssap_aln_line_parts[ 6 ] ) or None,
		amino_acid         =      ssap_aln_line_parts[ 5 ],
	 ) if right_is_present( ssap_aln_line_parts ) else None

def process_ssap_aln_line_parts(ssap_aln_line_parts):
	both_sides_present = left_is_present( ssap_aln_line_parts ) and right_is_present( ssap_aln_line_parts )
	return ssap_aln_entry(
		left_residue  = get_left_residue ( ssap_aln_line_parts ),
		right_residue = get_right_residue( ssap_aln_line_parts ),
		score         = float( ssap_aln_line_parts[ 4 ] ) if both_sides_present else None,
	)

def process_ssap_aln_line(ssap_aln_line):
	ssap_aln_line_parts = ssap_aln_line.split()
	if len( ssap_aln_line_parts ) != 9:
		raise Exception("Couldn't find 9 parts in SSAP alignment line " + ssap_aln_line )
	return process_ssap_aln_line_parts( ssap_aln_line_parts )

def get_index_based_equiv_rows(parsed_ssap_aln_data):
	left_ctr  = 0
	right_ctr = 0
	result    = []
	for parsed_ssap_aln_row in parsed_ssap_aln_data:
		left_is_present  = parsed_ssap_aln_row.left_residue  != None
		right_is_present = parsed_ssap_aln_row.right_residue != None
		result.append( [
			left_ctr  if left_is_present  else None,
			right_ctr if right_is_present else None,
			parsed_ssap_aln_row.score
		] )
		if left_is_present:
			left_ctr  += 1
		if right_is_present:
			right_ctr += 1

	return result

def read_ssap_alignment(aln_filename):
	with open( aln_filename, 'r' ) as python_source_file:
		parsed_ssap_aln_data = [ process_ssap_aln_line( i ) for i in python_source_file.readlines() if not i.startswith( '#' ) ]

	left_seq_data  = pdb_sequence( [ i.left_residue  for i in parsed_ssap_aln_data if i.left_residue   != None ] )
	right_seq_data = pdb_sequence( [ i.right_residue for i in parsed_ssap_aln_data if i.right_residue  != None ] )

	result = alignment( 2 )
	for entry in get_index_based_equiv_rows( parsed_ssap_aln_data ):
		score = entry.pop()
		score = 1 # ************************ DON'T LEAVE THIS LIKE THIS !!! ***********************************
		result.append( entry, score )

	return [
		left_seq_data,
		right_seq_data,
		result,
	]

