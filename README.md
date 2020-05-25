# aln_gluing_python_experiment

Experiment in gluing protein sequence alignments

## Example of alignment to improve

Superfamily superposition of 3.30.1370.60 in v4.2

(which contains domains: 1nxuB02,1v9nA02,1wtjA02,1z2iA02,2g8yA02,3i0pA02,3uoeA02,4h8aA02)

The problem can be seen in the green/yellow region of the alignbow image here:

http://www.cathdb.info/version/latest/superfamily/3.30.1370.60/superposition

According to a previous email to myself, this is due to it being a pairwise alignment and the alignment of 1wtjA02 vs 1z2iA02 getting messed up by differences in unobserved regions.

## Type checking

~~~sh
ls -1 a.py cath/*.py test/*.py | entr -cs 'mypy --check-untyped-defs a.py cath/*.py test/*.py'
~~~

## cath-tools mod

To get the scores coming out of cath-tools to be out of 100:

~~~diff
diff --git a/source/uni/alignment/residue_score/residue_scorer.cpp b/source/uni/alignment/residue_score/residue_scorer.cpp
index d31d8829..2bb7bce0 100644
--- a/source/uni/alignment/residue_score/residue_scorer.cpp
+++ b/source/uni/alignment/residue_score/residue_scorer.cpp
@@ -162,7 +162,7 @@ alignment_residue_scores residue_scorer::get_alignment_residue_scores(const alig
 			if ( has_position_of_entry_of_index( arg_alignment, entry_ctr, index_ctr ) ) {
 				const float_score_type &numerator   = numerators  [ entry_ctr ][ index_ctr ];
 				const float_score_type &denominator = denominators[ entry_ctr ][ index_ctr ];
-				scores[ entry_ctr ][ index_ctr ] = ( denominator != 0.0 ) ? ( numerator / denominator ) : 0.0;
+				scores[ entry_ctr ][ index_ctr ] = ( denominator != 0.0 ) ? ( 100.0 * numerator / denominator ) : 0.0;
 			}
 		}
 	}
~~~
