import csv, sqlite3

#Create connection object to our database file 
con = sqlite3.connect("Database.db")

#Create a cursor object to accurate find data in the database
cur = con.cursor()

#Creating the Kinase table of our database with all of its column names 
cur.execute('''CREATE TABLE Kinase 
	(Kinase_Gene_Name VARCHAR(30), Kinase_Protein_Name VARCHAR(255), Kinase_Group VARCHAR(8), Family VARCHAR(15), SubFamily VARCHAR(10), 
	Uniprot_ID PRIMARY KEY, UniProt_Entry VARCHAR(20),  Alias VARCHAR(255), Subcellular_Location VARCHAR(255));''')

#Reading our Kinase_Table csv, setting up its contents as a dictionary and setting it up in a format to be fitted into the Kinase table of our database
with open('Kinase_Table.csv','rt') as Kin: 
    dr = csv.DictReader(Kin)
    to_db = [(i['Kinase_Gene_Name'], i['Kinase_Protein_Name'], i['Kinase_Group'], i['Family'], i['SubFamily'], i['Uniprot_ID'], i['UniProt_Entry'], 
    	i['Alias'], i['Subcellular_Location']) for i in dr]

#Running a cursor command to populate our Kinase table with all of the data from our Kinase_Table.csv
cur.executemany('''INSERT INTO Kinase 
	(Kinase_Gene_Name, Kinase_Protein_Name, Kinase_Group, Family, SubFamily, Uniprot_ID, UniProt_Entry, Alias, Subcellular_Location) 
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);''', to_db)

#Commit the changes
con.commit()

# We then repeat the previous three steps to create, prepare and populate PhoshoSites and Inhibitors tables for our database

cur.execute('''CREATE TABLE PhosphoSites 
	(PHOSPHO_ID PRIMARY KEY, KINASE_GENE_NAME VARCHAR(50), KIN_UNIPROT_ID VARCHAR(10), SUBSTRATE_NAME VARCHAR(50), SUB_UNIPROT_ID VARCHAR(10),
	SUB_GENE_NAME VARCHAR(50), SUB_MOD_RSD VARCHAR(10), SITE_7_AA VARCHAR(15), CHR_LOC VARCHAR(20), SUB_ENTRY_NAME VARCHAR(30));''')

with open('Phosphosite_Table.csv','rt') as Pho: # `with` statement available in 2.5+
    #csv.DictReader uses first line in file for column headings by default
    dr1 = csv.DictReader(Pho) # comma is default delimiter
    to_db1 = [(i['PHOSPHO_ID'], i['KINASE_GENE_NAME'], i['KIN_UNIPROT_ID'], i['SUBSTRATE_NAME'], i['SUB_UNIPROT_ID'], i['SUB_GENE_NAME'], 
    	i['SUB_MOD_RSD'], i['SITE_7_AA'], i['CHR_LOC'], i['SUB_ENTRY_NAME']) for i in dr1]

cur.executemany('''INSERT INTO PhosphoSites 
	(PHOSPHO_ID, KINASE_GENE_NAME, KIN_UNIPROT_ID, SUBSTRATE_NAME, SUB_UNIPROT_ID, SUB_GENE_NAME, SUB_MOD_RSD, SITE_7_AA, CHR_LOC, SUB_ENTRY_NAME) 
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', to_db1)

con.commit()

cur.execute('''CREATE TABLE Inhibitors 
	(INHIBITOR_ID PRIMARY KEY, INN_Name VARCHAR(30), Targets VARCHAR(20), RoF INTEGER, MW INTEGER, LogP INTEGER, TPSA INTEGER, HBA INTEGER, HBD INTEGER,
	NRB INTEGER, Smiles VARCHAR(255), InChi_Key VARCHAR(255), ChEMBL_ID VARCHAR(20), image_link VARCHAR(255));''') 

with open('Inhibitor_Table.csv','rt') as Inh: # `with` statement available in 2.5+
    #csv.DictReader uses first line in file for column headings by default
    dr2 = csv.DictReader(Inh) # comma is default delimiter
    to_db2 = [(i['INHIBITOR_ID'], i['INN_Name'], i['Targets'], i['RoF'], i['MW'], i['LogP'], i['TPSA'], i['HBA'], i['HBD'], i['NRB'], i['Smiles'], 
    	i['InChi_Key'],i['ChEMBL_ID'], i['image_link']) for i in dr2]

cur.executemany('''INSERT INTO Inhibitors 
	(INHIBITOR_ID, INN_Name, Targets, RoF, MW, LogP, TPSA, HBA, HBD, NRB, Smiles, InChi_Key, ChEMBL_ID, image_link) 
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', to_db2)

con.commit()

#As there are many to many connections between Kinases-Phosphosites and Kinase-Inhibitors we need to set up relational tables in between each respective
#pair of tables, for more efficient querying between two tables.

#We create our first relational table to connect our Kinase and Phosphosites tables together with each column acting as a foreign key referencing to the 
#two tables primary keys. 
cur.execute('''CREATE TABLE Kin_Pho_Interaction 
	(KinPhoID INTEGER PRIMARY KEY, Kin VARCHAR(255), Pho INTEGER, 
	FOREIGN KEY(Kin) REFERENCES Kinase(UniProt_ID), FOREIGN KEY(Pho) REFERENCES PhosphoSites(PHOSPHO_ID));''')

con.commit()

#We then popluate our relational table with the values from both our Kinase and Phosphosites table via. the common column between the two i.e Kinase Uniprot
#ID 
cur.execute('''INSERT INTO Kin_Pho_Interaction (Kin, Pho)
SELECT Kinase.UniProt_ID, PhosphoSites.PHOSPHO_ID FROM Kinase INNER JOIN PhosphoSites
ON Kinase.UniProt_ID = PhosphoSites.KIN_UNIPROT_ID ;''')

con.commit()

#We then do the above two steps to setup and populate our relational table between Kinase and Inhibitors.

cur.execute('''CREATE TABLE Kin_Inh_Interaction 
	(InteractionID INTEGER PRIMARY KEY, Kina VARCHAR(255) , Inhi VARCHAR(255), 
	FOREIGN KEY(Kina) REFERENCES Kinase(UniProt_ID), FOREIGN KEY(Inhi) REFERENCES Inhibitors(INHIBITOR_ID));''')

con.commit()

cur.execute('''INSERT INTO Kin_Inh_Interaction (Kina, Inhi)
SELECT Kinase.UniProt_ID, Inhibitors.INHIBITOR_ID FROM Kinase INNER JOIN Inhibitors
ON Kinase.Kinase_Gene_Name = Inhibitors.Targets ;''')

con.commit()


#Finally we connect all of our database tables together to complete our database. Connections are made between:

#Our Kinase table and our Kinase-Inhibitor relation table 
cur.execute("SELECT Kina FROM Kin_Inh_Interaction INNER JOIN Kinase ON Kinase.UniProt_ID = Kin_Inh_Interaction.Kina ;")
con.commit()

#Our Inhibitor table and our Kinase-Inhibitor relation table 
cur.execute("SELECT Inhi FROM Kin_Inh_Interaction INNER JOIN Inhibitors ON Inhibitors.INHIBITOR_ID = Kin_Inh_Interaction.Inhi ;")
con.commit()

#Our Kinase table and our Kinase-Phosphosite relation table 
cur.execute("SELECT Kin FROM Kin_Pho_Interaction INNER JOIN Kinase ON Kinase.UniProt_ID = Kin_Pho_Interaction.Kin ;")
con.commit()

#Our Phosphosite table and our Kinase-Phosphosite relation table 
cur.execute("SELECT Pho FROM Kin_Pho_Interaction INNER JOIN PhosphoSites ON PhosphoSites.PHOSPHO_ID = Kin_Pho_Interaction.Pho ;")
con.commit()

con.close()