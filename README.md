GEXF-generator
==============

This repository contains a simple script to generate network files from any TAB-delimited observation matrix.

(this is a draft README file, more information and examples will follow)

Environment file is the expected input file, which consists of three columns that are separated from each other by a TAB character: unit, sample and count. Unit can be any unit (taxonomy, functions, OTU IDs, etc). Sample column contains sample names. Count column contains number of observations for a given unit in a sample. Samples directory contains an example environment file.

You can generate an environment file from an observation matrix using the script in the scripts directory. The only input it expects is a counts matrix, which should have sample names in the first column, and unit names in the first row.

A mapping file will generate an XML file with much more information that can be used for visualization purposes from within Gephi. An example mapping file can also be found in samples directory. Briefly, the first column of the mapping file should be identical to the observation matrix. Any category listed in this file will appear in drop boxes in Gephi. Keyword "color" identifies a special column in this file. HTML colors given in this column color samples in Gephi directly.

If you expect more from this script, please let me know. You can send your e-mails to meren@mbl.edu.
