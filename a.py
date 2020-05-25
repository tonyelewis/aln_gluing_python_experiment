#!/usr/bin/env python3

# Do direct align twice
# Store "either" score when gluing
# Use "either" scores if/when adding the penalties
#
# `--strength-over-consensus-preference` : raise each score by 2^x
# `--strength-over-length-preference`    : calc penalty for window by summing violation scores raise by by 2^y
#                                          (possibly capping the y to be >=0 for the max score)
#                                          then apply normal n^(2^x) as above

import os

from itertools import product
from os        import listdir
from pathlib   import Path
from typing    import List

from cath.aln        import alignment
from cath.aln_matrix import aln_matrix
from cath.multi_aln  import glue_from_aln_matrix

def get_aln_filenames_in_dir(dir,suffix='.list'):
	return sorted( [ i for i in os.listdir( dir ) if i.endswith( suffix ) ] )

def get_sorted_ids_of_aln_filenames(aln_filenames) -> List[str]:
	ids = set()
	for aln_filename in aln_filenames:
		ids_part = aln_filename.split( '.' )[0]
		ids.add( ids_part[ :7 ] )
		ids.add( ids_part[ 7: ] )
	return sorted(ids)

# example_dir   = Path( os.environ['HOME'] ) / '/temp_nathalie_ebi/cath-tools.tmp.CE55F4AEDEEC2A20_1A94EFEA7BDF2080'
# example_dir   = Path( os.environ['HOME'] ) / '/temp_nathalie_ebi/refined_alignments'
example_dir   = Path( os.environ['HOME'] ) / '/temp_nathalie_ebi/refined_alignments_cent'

aln_filenames = get_aln_filenames_in_dir       ( example_dir   )
ids           = get_sorted_ids_of_aln_filenames( aln_filenames )

the_matrix    = aln_matrix( ids )
the_matrix.read_alignments( example_dir )

glue_from_aln_matrix( the_matrix )

# 1 '3aj4A00' 9 '1eazA00'
# 9 '1eazA00' 2 '1xodB00'