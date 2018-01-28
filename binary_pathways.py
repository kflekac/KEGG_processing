'''
coding: utf-8
confidence_filtering.py
version 2.0
author: Kahli Flekac, @kflekac
usage: binary_pathways.py

Reads in the KEGG pathways files (generated by getPathwayList.py, Author:
    Yuke Yan, 2015) and the KEGG pathway/gene list for your organism of choice 
    (as generated by getPathway_Gene.py, Author: Yuke Yan, 2015) creates a
    binary association file for each pathway/gene.

Dependencies:
    python 2.7.13
    pandas v_0.20.3-py27_0

Inputs:
    + *.csv file generated by getPathwayList.py. File contains 2 columns:
            [0] PathID: KEGG pathway IDs
            [1] Description: KEGG pathway names
    + *.csv file generated by getPathway_Gene.py. Contains 2 non-unique columns:
            [0] PathID: KEGG pathway IDs
            [1] GeneID: GeneID of gene associated with that pathway

Outputs:
    + *.csv file containing binary-coded pathway associations for each gene/pathway.

'''

import os
import sys
import pandas as pd


# Functions
# Log a message to stderr
def msg(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Log an error to stderr and quit with non-zero error code
def err(*args, **kwargs):
    msg(*args, **kwargs)
    sys.exit(1);

# Check file exists
def check_file(f):
    return os.path.isfile(f)


#==========================
# change as required
#==========================
#File names
genes_file = 'human_pathways_genes.csv'
pathway_file = "human_pathways_all.csv"
out_file = "./out_files/KEGG_binary_pathways.csv"

#==========================

#Checking files exist
if not check_file(full_ppi_path):
    err('ERROR: Cannot find "{}". Check file exists in the specified directory.'.format(genes_file))

if not check_file(network_ppi_path):
    err('ERROR: Cannot find "{}". Check file exists in the specified directory.'.format(pathway_file))

#Cleaning input and create a dictionary of pathway names
pathway_df = pd.read_csv(pathway_file)
pathway_df["Description"] = pathway_df["Description"].apply(lambda x: x.split(" - ")[0])

#Creating the column names for the binary file
pathway_names = dict()
for i in range(pathway_df.shape[0]):
    pathway_names[pathway_df['PathID'][i]] = pathway_df['PathID'][i] +": " + pathway_df['Description'][i]


# The genes and pathway associations
human_genes = pd.read_csv(genes_file)

# Removing "hsa:" str from GeneID
human_genes['GeneID'] = human_genes['GeneID'].apply(lambda x: x.split(":")[1])
human_genes.head()


# Creating dataframe of 0's
binary_df = pd.DataFrame(0, index = human_genes['GeneID'].unique(), columns=pathway_names.values())
# Replacing with 1's where pathway/gene in genes_file
for i in range(human_genes.shape[0]):
    binary_df.at[human_genes['GeneID'][i], pathway_names[human_genes['PathID'][i]]] = 1

#Adding another column/row containing sum of gene/pathway involvement
binary_df['Total Pathways'] = binary_df.sum(axis = 1)
binary_df["Total Pathways"] = binary_df["Total Pathways"].astype(int, copy = False)

tot = binary_df.apply(sum, axis = 0); tot.name = "Total Genes"
binary_df = binary_df.append(tot)

binary_df = binary_df.reset_index()
binary_df.rename(columns = {'index':'GeneID'}, inplace = True)
binary_df.at[7127,"Total Pathways"] = None

# Writing file
binary_df.to_csv(out_file, index= False)
