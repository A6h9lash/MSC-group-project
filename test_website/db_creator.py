import csv, sqlite3

con = sqlite3.connect("11.db")
cur = con.cursor()
cur.execute("CREATE TABLE Kinase (Kinase_Gene_Name PRIMARY KEY, Kinase_Protein_Name VARCHAR(250), Kinase_Group VARCHAR(250), Family VARCHAR(250), SubFamily VARCHAR(250), UniProt_ID VARCHAR(250), UniProt_Entry VARCHAR(250), Subcellular_Location VARCHAR(255), Alias VARCHAR(255));") 
with open('Kinase_Table.csv','rt') as fin: # `with` statement available in 2.5+
    #csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['Kinase_Gene_Name'], i['Kinase_Protein_Name'], i['Kinase_Group'], i['Family'], i['SubFamily'], i['UniProt_ID'], i['UniProt_Entry'], i['Subcellular_Location'], i['Alias'] ) for i in dr]

cur.executemany("INSERT INTO Kinase (Kinase_Gene_Name, Kinase_Protein_Name, Kinase_Group, Family, SubFamily, UniProt_ID, UniProt_Entry, Subcellular_Location, Alias) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
con.commit()

cur.execute("CREATE TABLE PhosphoSites (PHOSPHO_ID PRIMARY KEY, Kin_Gene_Name VARCHAR(255), KIN_ACC_ID VARCHAR(255), Substrate_Name VARCHAR(255), Substrate_UniProt_ID VARCHAR(255), Substrate_Gene_Name VARCHAR(255), Substrate_UniProt_Entry VARCHAR(255), Substrate_Modified_Residue VARCHAR(255), Neighbouring_Sequence VARCHAR(255), Human_Chromosome_Location VARCHAR(255));") 
with open('Phospho_Table_FINAL.csv','rt') as fin1: # `with` statement available in 2.5+
    #csv.DictReader uses first line in file for column headings by default
    dr1 = csv.DictReader(fin1) # comma is default delimiter
    to_db1 = [(i['PHOSPHO_ID'], i['Kin_Gene_Name'], i['KIN_ACC_ID'], i['Substrate_Name'], i['Substrate_UniProt_ID'], i['Substrate_Gene_Name'], i['Substrate_UniProt_Entry'], i['Substrate_Modified_Residue'], i['Neighbouring_Sequence'], i['Human_Chromosome_Location']) for i in dr1]

cur.executemany("INSERT INTO PhosphoSites (PHOSPHO_ID, Kin_Gene_Name, KIN_ACC_ID, Substrate_Name, Substrate_UniProt_ID, Substrate_Gene_Name, Substrate_UniProt_Entry, Substrate_Modified_Residue, Neighbouring_Sequence, Human_Chromosome_Location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db1)
con.commit()

cur.execute("CREATE TABLE Inhibitors (INN_Name PRIMARY KEY, ChEMBL_ID VARCHAR(255), Smiles VARCHAR(255), InCHI_Key VARCHAR(255), RoF VARCHAR(255), Molecular_Weight VARCHAR(255), LogP VARCHAR(255), TPSA VARCHAR(255), HBA VARCHAR(255), HBD VARCHAR(255), NRB VARCHAR(255), Image VARCHAR(255), Targets VARCHAR(255));") 
with open('Inhibitor_final.csv','rt') as fin2: # `with` statement available in 2.5+
    #csv.DictReader uses first line in file for column headings by default
    dr2 = csv.DictReader(fin2) # comma is default delimiter
    to_db2 = [(i['INN_Name'], i['ChEMBL_ID'], i['Smiles'], i['InCHI_key'], i['RoF'], i['Molecular_Weight'], i['LogP'], i['TPSA'], i['HBA'], i['HBD'], i['NRB'], i['Image'], i['Targets']) for i in dr2]

cur.executemany("INSERT INTO Inhibitors (INN_Name, ChEMBL_ID, Smiles, InCHI_key, RoF, Molecular_Weight, LogP, TPSA, HBA, HBD, NRB, Image, Targets) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db2)
con.commit()

#Joining Kinase and Phosphosite tables

cur.execute("SELECT Kinase_Gene_Name FROM Kinase INNER JOIN PhosphoSites ON PhosphoSites.Kin_Gene_Name = Kinase.Kinase_Gene_Name ;")
con.commit()

#Joining Kinase and Inhibitor tables

cur.execute("SELECT Targets FROM Inhibitors INNER JOIN Kinase ON Kinase.Kinase_Gene_Name = Inhibitors.Targets ;")
con.commit()

con.close()