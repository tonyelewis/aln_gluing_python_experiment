from collections import namedtuple
from typing      import Dict, Iterable, List

pdb_residue = namedtuple('pdb_residue', [ 'pdb_residue_number', 'pdb_insert_code', 'amino_acid' ])

def _residue_id_of_residue_tuple(residue: pdb_residue) -> str:
	return (
		str( residue.pdb_residue_number )
		+
		( residue.pdb_insert_code if residue.pdb_insert_code is not None else '' )
	)

class pdb_sequence:
	def __init__(self, prm_residues : Iterable[pdb_residue] = [] ) -> None:
		self.residues: List[pdb_residue] = list( prm_residues )

	def __len__(self):
		return len( self.residues )

	def __contains__(self, item):
		return self.residues[ item ]

	def __getitem__(self, key):
		return self.residues[ key ]

	def append(self,residue: pdb_residue):
		self.residues.append( residue )

	def seq_string(self) -> str:
		return ''.join( [ x.amino_acid for x in self.residues ] )
	
	def res_ids(self):
		return [ _residue_id_of_residue_tuple( x ) for x in self.residues ]

	def __eq__(self,rhs) :
		return self.residues == rhs.residues
