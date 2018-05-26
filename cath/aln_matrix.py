from itertools import product
from os        import path
from typing    import List, Tuple

from . import aln
from . import pdb_sequence

def less_to_key(is_less_than):
	'Convert a less_than= function into a key= function'
	class K:
		def __init__(self, obj, *args):
			self.obj = obj
		def __lt__(self, other):
			return is_less_than( self.obj, other.obj )
		def __gt__(self, other):
			return is_less_than(other.obj, self.obj)
		def __ne__(self, other):
			return self.__lt__( self.obj, other.obj ) or self.__gt__( other.obj, self.obj )
		def __eq__(self, other):
			return not self.__ne__( self.obj, other.obj )
		def __le__(self, other):
			return not self.__gt__( self.obj, other.obj )
		def __ge__(self, other):
			return not self.__lt__( self.obj, other.obj )
	return K

def _aln_file(dir,id1,id2,suffix):
	return path.join( dir, id1 + id2 + suffix )

def _aln_file_exists(dir,id1,id2,suffix):
	return path.exists( _aln_file( dir, id1, id2, suffix ) )


class aln_matrix:
	def __init__(self, ids):
		self.ids        = sorted(ids)
		self.seqs       =   [ None for x in range( len( self.ids ) ) ]
		self.alignments = [ [ None for x in range( len( self.ids ) ) ] for x in range( len( self.ids ) ) ]
		self._reset_indices_of_id()

	def _reset_indices_of_id(self):
		self.index_of_id = dict( ( id, idx ) for ( idx, id ) in enumerate( self.ids ) )

	def num_entries(self):
		return len(self.ids)

	def length_of(self,entry_index):
		return len( self.seqs[ entry_index ] )

	def _insert_or_check_seq(self,index,seq):
		if self.seqs[ index ] is None:
			self.seqs[ index ] = seq
		else:
			if self.seqs[ index ] != seq:
				raise Exception("Sequences contradict for " + self.ids[ index ] )

	# This is a hack that *assumes* a half-matrix of some ordering is present in its call to sort()
	# to reorder the list to its original order
	def read_alignments(self,dir,suffix='.list'):
		self.ids.sort( key=less_to_key( lambda x, y: _aln_file_exists( dir, x, y, suffix ) ) )

		# MAX_MATRIX_DIM_SIZE = 10
		MAX_MATRIX_DIM_SIZE = 20
		del self.ids[ MAX_MATRIX_DIM_SIZE: ]

		for (index_a, index_b) in product(range(len(self.ids)), range(len(self.ids))):
			if index_a >= index_b:
				continue
			print( index_a, index_b )
			id_a = self.ids[ index_a ]
			id_b = self.ids[ index_b ]
			file = path.join( dir, id_a + id_b + suffix)
			[seq_a, seq_b, alignment] = aln.read_ssap_alignment( _aln_file( dir, id_a, id_b, suffix ) )

			self._insert_or_check_seq( index_a, seq_a )
			self._insert_or_check_seq( index_b, seq_b )

			self.alignments[ index_a ][ index_b ] = alignment
			self.alignments[ index_b ][ index_a ] = aln.flip_copy( alignment )

	def get_str_of_pseudo_alignment(self, pseudo_alignment: List[Tuple[int]]) -> str:
		if not len( pseudo_alignment ):
			return ''
		seq_strs = [ str() for i in pseudo_alignment[0] ]
		for index, _ in enumerate(pseudo_alignment):
			for entry, _ in enumerate(pseudo_alignment[index]):
				seq_index = pseudo_alignment[index][entry]
				letter = self.seqs[entry][seq_index].amino_acid if seq_index is not None else '-'
				seq_strs[entry] += letter
		result = str()
		for entry, _ in enumerate(pseudo_alignment[index]):
			result += '>' + self.ids[ entry ] + "\n"
			result += seq_strs[entry] + "\n"
		# print(repr(pseudo_alignment))
		# print(repr(seq_strs))
		# print(result)
		# exit()
		return result


