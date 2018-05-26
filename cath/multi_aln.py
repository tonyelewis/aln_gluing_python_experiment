from itertools import chain, product
from numpy     import prod
from enum      import Enum, auto
from typing    import Iterable, List, Tuple

from .aln              import alignment
from .aln_matrix       import aln_matrix
from .multi_equiv_list import entry_res_id, get_psuedo_alignment, multi_equiv_list

class ScoreComboMethod(Enum):
	MAX       = auto()
	GEOM_MEAN = auto()
	MIN       = auto()

def combine_scores(method: ScoreComboMethod, *scores: float) -> float:
	if not len( scores ):
		raise Exception("Can't combine empty list of scores")
	if None in scores:
		return None
	if method == ScoreComboMethod.GEOM_MEAN:
		return prod( scores ) ** ( 1.0 / len( scores ) )
	if method == ScoreComboMethod.MAX:
		return max( scores )
	if method == ScoreComboMethod.MIN:
		return min( scores )
	raise Exception("Unrecognised ScoreComboMethod")

def glued_alignments(aln_lhs : alignment, aln_rhs : alignment, method : ScoreComboMethod = ScoreComboMethod.GEOM_MEAN):

	def co_iterate_gen_exp(align_lhs : List, align_rhs : List):
		lhs_links = ( ( *x[ 0 ], x[ 1 ] ) for x in zip( aln_lhs.equiv_rows, aln_lhs.scores ) )
		rhs_links = ( ( *x[ 0 ], x[ 1 ] ) for x in zip( aln_rhs.equiv_rows, aln_rhs.scores ) )
		try:
			while True:
				lhs_link = next( lhs_links )
				rhs_link = next( rhs_links )
				while lhs_link[ 1 ] is None or rhs_link[ 0 ] is None or lhs_link[ 1 ] != rhs_link[ 0 ]:
					while lhs_link[ 1 ] is None or ( rhs_link[ 0 ] is not None and lhs_link[ 1 ] < rhs_link[ 0 ] ):
						if lhs_link[ 0 ] is not None:
							yield( lhs_link[ 0 ], None, None )
						lhs_link = None
						lhs_link = next( lhs_links )
					while rhs_link[ 0 ] is None or ( lhs_link[ 1 ] is not None and rhs_link[ 0 ] < lhs_link[ 1 ]  ):
						if rhs_link[ 1 ] is not None:
							yield( None, rhs_link[ 1 ], None )
						rhs_link = None
						rhs_link = next( rhs_links )
				if lhs_link[ 0 ] is not None or rhs_link[ 1 ] is not None:
					yield ( lhs_link[ 0 ], rhs_link[ 1 ], combine_scores( method, lhs_link[ 2 ], rhs_link[ 2 ] ) )
					lhs_link = None
					rhs_link = None
		except StopIteration:
			try:
				while True:
					if lhs_link is not None and lhs_link[ 0 ] is not None:
						yield( lhs_link[ 0 ], None, None )
					lhs_link = next( lhs_links )
			except StopIteration:
				pass

			try:
				while True:
					if rhs_link is not None and rhs_link[ 1 ] is not None:
						yield( None, rhs_link[ 1 ], None )
					rhs_link = next( rhs_links )
			except StopIteration:
				pass

	result = alignment( 2 )
	for row in co_iterate_gen_exp( aln_lhs.equiv_rows, aln_rhs.equiv_rows ):
		result.append( ( row[ 0 ], row[ 1 ] ), row[ 2 ] )
	
	return result

def intermediate_aligns_gen_exp(aln_matrix: aln_matrix, index_a: int, index_b: int):
	# Yield the direct alignment twice
	yield aln_matrix.alignments[ index_a ][ index_b ]
	yield aln_matrix.alignments[ index_a ][ index_b ]

	# ...and then loop over all intermediate alignments
	for non_a_non_b_index in range( aln_matrix.num_entries() ):
		if non_a_non_b_index not in ( index_a, index_b ):
			yield glued_alignments(
				aln_matrix.alignments[ index_a           ][ non_a_non_b_index ],
				aln_matrix.alignments[ non_a_non_b_index ][ index_b           ],
			)

def get_candidate_links_for_entry_pair(matrix: aln_matrix, index_lhs: int, index_rhs: int) -> List:
	if index_lhs == index_rhs:
		raise Exception("Cannot get_candidate_links_for_entry_pair() for an entry with itself")
	length_lhs = matrix.length_of( index_lhs )
	length_rhs = matrix.length_of( index_rhs )
	links_lhs  = [ set() for i in range( length_lhs ) ] # type: List
	links_rhs  = [ set() for i in range( length_rhs ) ] # type: List

	def add_links(alignment: alignment) -> None:
		for equiv_row in alignment.equiv_rows:
			( equiv_lhs, equiv_rhs ) = equiv_row
			if equiv_lhs is not None and equiv_rhs is not None:
				links_lhs[ equiv_lhs ].add( equiv_rhs )
				links_rhs[ equiv_rhs ].add( equiv_lhs )

	for intermediate_aln in intermediate_aligns_gen_exp( matrix, index_lhs, index_rhs ):
		add_links( intermediate_aln )

	list_lhs = []
	for index_lhs in range( len( links_lhs ) ):
		for index_rhs in sorted( links_lhs[ index_lhs ] ):
			list_lhs.append( ( index_lhs, index_rhs, ) )

	return sorted( list_lhs )

def score_candidate_links(matrix: aln_matrix, index_lhs: int, index_rhs: int, unscored_links: List) -> List:
	scores = [ 0.0 for i in range( len( unscored_links ) )]

	for intermediate_aln in intermediate_aligns_gen_exp( matrix, index_lhs, index_rhs ):
		for ( ctr, ( link_lhs_idx, link_rhs_idx ) ) in enumerate( unscored_links ):
			lhs_equivs_idx = intermediate_aln.aln_index_by_index_per_entry[ 0 ][ link_lhs_idx ]
			rhs_equivs_idx = intermediate_aln.aln_index_by_index_per_entry[ 1 ][ link_rhs_idx ]
			score = 0.0
			if lhs_equivs_idx == rhs_equivs_idx:
				if intermediate_aln.scores[ lhs_equivs_idx ] is not None:
					score += intermediate_aln.scores[ lhs_equivs_idx ]
				else:
					raise Exception("argh")
			else:
				def get_score_of_between(between_idx: int) -> int:
					inter_score = intermediate_aln.scores[ between_idx ] if intermediate_aln.scores[ between_idx ] is not None else float('-inf')
					return inter_score

				score -= max(
					0.0,
					get_score_of_between(max(
						range( min( lhs_equivs_idx, rhs_equivs_idx ), max( lhs_equivs_idx, rhs_equivs_idx ) + 1 ),
						key=get_score_of_between,
					))
				)
			scores[ ctr ] += score
			# print(
			# 	  ( "%3d" % ctr )
			# 	+ " - ( "
			# 	+ ( "%3d" % link_lhs_idx     )
			# 	+ ", "
			# 	+ ( "%3d" % link_rhs_idx     )
			# 	+ " ) -> ( "
			# 	+ ( "%3d" % lhs_equivs_idx   )
			# 	+ ", "
			# 	+ ( "%3d" % rhs_equivs_idx   )
			# 	+ " ) : "
			# 	+ ( "%.2f" % + score         )
			# 	+ " into "
			# 	+ ( "%.2f" % + scores[ ctr ] )
			# )
		# print()

	scored_links = [(i,j,s) for ((i,j),s) in zip( unscored_links, scores ) ]
	scored_links.sort( reverse=True, key=lambda x: x[ 2 ] )
	return scored_links

def get_scored_candidate_links_for_entry_pair(matrix: aln_matrix, index_lhs: int, index_rhs: int) -> List:
	candidate_links = get_candidate_links_for_entry_pair( matrix, index_lhs, index_rhs )
	return score_candidate_links( matrix, index_lhs, index_rhs, candidate_links )

def get_indexed_scored_candidate_links_for_entry_pair(matrix: aln_matrix, index_lhs: int, index_rhs: int) -> Iterable[Tuple[int,int,int,int,float]]:
	return (
		    ( index_lhs, index_rhs, i, j, score )
		for i, j, score
		in  get_scored_candidate_links_for_entry_pair( matrix, index_lhs, index_rhs )
	)

def get_scored_candidate_links(matrix: aln_matrix) -> List[Tuple[int,int,int,int,float]]:
	return list( chain.from_iterable(
		    get_indexed_scored_candidate_links_for_entry_pair( matrix, index_lhs, index_rhs)
		for index_lhs, index_rhs
		in  product( range( matrix.num_entries() ), range( matrix.num_entries() ) )
		if  index_lhs < index_rhs
	) )

def glue_from_aln_matrix(matrix: aln_matrix) -> None:
	candidate_links = get_scored_candidate_links( matrix )
	candidate_links = sorted( get_scored_candidate_links( matrix ), reverse=True, key=lambda x: x[ 4 ] )

	lengths_genexp = [ len( i ) for i in matrix.seqs if i is not None ]
	print(repr(lengths_genexp))
	meq = multi_equiv_list( *lengths_genexp )

	for ( ctr, ( entry_a, entry_b, index_a, index_b, score ) ) in enumerate(candidate_links):
		# print(repr([entry_a, entry_b, index_a, index_b, score]))
		try:
			meq.link( entry_res_id( entry_a, index_a ), entry_res_id( entry_b, index_b ) )
		except:
			pass
		if ctr % 100 == 0:
			print(matrix.get_str_of_pseudo_alignment(get_psuedo_alignment(meq)))
			print(score)
	print(matrix.get_str_of_pseudo_alignment(get_psuedo_alignment(meq)))
	exit()


