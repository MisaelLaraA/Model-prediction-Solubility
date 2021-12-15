
from typing_extensions import ParamSpec
import PIL
import numpy as np
import pandas as pd
import streamlit as st
import pickle
from PIL import Image
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import Draw



## Calculate molecular descriptors
def AromaticProportion(m):
  aromatic_atoms = [m.GetAtomWithIdx(i).GetIsAromatic() for i in range(m.GetNumAtoms())]
  aa_count = []
  for i in aromatic_atoms:
    if i==True:
      aa_count.append(1)
  AromaticAtom = sum(aa_count)
  HeavyAtom = Descriptors.HeavyAtomCount(m)
  AR = AromaticAtom/HeavyAtom
  return AR

def generate(smiles, verbose=False):

    moldata= []
    for elem in smiles:
        mol=Chem.MolFromSmiles(elem)
        moldata.append(mol)

    baseData= np.arange(1,1)
    i=0
    for mol in moldata:

        desc_MolLogP = Descriptors.MolLogP(mol)
        desc_MolWt = Descriptors.MolWt(mol)
        desc_NumRotatableBonds = Descriptors.NumRotatableBonds(mol)
        desc_AromaticProportion = AromaticProportion(mol)

        row = np.array([desc_MolLogP,
                        desc_MolWt,
                        desc_NumRotatableBonds,
                        desc_AromaticProportion])

        if(i==0):
            baseData=row
        else:
            baseData=np.vstack([baseData, row])
        i=i+1

    columnNames=["MolLogP","MolWt","NumRotatableBonds","AromaticProportion"]
    descriptors = pd.DataFrame(data=baseData,columns=columnNames)

    return descriptors


image = Image.open('MOLECULE.png')

st.image(image, use_column_width=True)

st.write("""
Reference [ESOL:  Estimating Aqueous Solubility Directly from Molecular Structure](https://pubs.acs.org/doi/10.1021/ci034243x). ***J. Chem. Inf. Comput. Sci.*** 2004, 44, 3, 1000-1005
https://doi.org/10.1002/1520-6017.
***
""")




st.sidebar.header('Draw your molecule usaging SMILES Input ex Methanol CO')

## Read SMILES input
SMILES_input = 'CCO \n C \n CCCO'

SMILES = st.sidebar.text_area("Your Input here", SMILES_input)
SMILES = "C\n" + SMILES   #Adds C as a dummy, first item
SMILES = SMILES.split('\n')
st.header('Input you molecule in format SMILES')
SMILES[1:] 

## Calculate molecular descriptors
st.header('Molecular descriptors calculated')
X = generate(SMILES)
X[1:] # Skips the dummy first item


# Reads in saved model
load_model = pickle.load(open('solubility_model.pkl', 'rb'))

# Apply model to make predictions
prediction = load_model.predict(X)
#prediction_proba = load_model.predict_proba(X)

st.header('Calculated LogS values')
prediction[1:] # Skips the dummy first item

filemolecule = Chem.MolFromSmiles(SMILES_input)
Chem.MolToMolFile(filemolecule, 'moleculefile.mol')
m = Chem.MolFromSmiles(SMILES_input[1:])
mm = Chem.MolFromSmiles(SMILES_input[0:1])
Draw.MolToFile(m,'x.png')

Draw.MolToFile(mm,'xx.png')
st.image('x.png')

st.image('xx.png')

mmm = Chem.MolFromSmiles(SMILES_input)
Draw.MolToFile(mmm,'xxx.png')
st.image('xxx.png')