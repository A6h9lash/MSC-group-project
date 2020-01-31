from app import db

class Kinase(db.Model):

    __tablename__ = "Kinase"

    Kinase_Gene_Name = db.Column('Kinase_Gene_Name', db.String, primary_key = True)
    Kinase_Protein_Name = db.Column('Kinase_Protein_Name', db.String)
    Kinase_Group = db.Column('Kinase_Group', db.String)
    Family = db.Column('Family', db.String)
    Subfamily = db.Column('Subfamily', db.String)
    UniProt_ID = db.Column('UniProt_ID', db.String)
    UniProt_Entry = db.Column('UniProt_Entry', db.String)
    Subcellular_Location = db.Column('Subcellular_Location', db.String)
    Alias = db.Column('Alias', db.String)

class Phosphosite(db.Model):

    __tablename__ = "PhosphoSites"

    PHOSPHO_ID = db.Column('PHOSPHO_ID', db.Integer, primary_key = True)
    Kin_Gene_Name = db.Column('Kin_Gene_Name', db.String)
    KIN_ACC_ID = db.Column('KIN_ACC_ID', db.String)
    Substrate_Name = db.Column('Substrate_Name', db.String)
    Substrate_UniProt_ID = db.Column('Substrate_UniProt_ID', db.String)
    Substrate_Gene_Name = db.Column('Substrate_Gene_Name', db.String)
    Substrate_UniProt_Entry = db.Column('Substrate_UniProt_Entry', db.String)
    Substrate_Modified_Residue = db.Column('Substrate_Modified_Residue', db.String)
    Neighbouring_Sequence = db.Column('Neighbouring_Sequence', db.String)
    Human_Chromosome_Location = db.Column('Human_Chromosome_Location', db.String)

class Inhibitors(db.Model):
	
    __tablename__ = "Inhibitors"

    INN_Name = db.Column('INN_Name', db.String, primary_key = True)
    ChEMBL_ID = db.Column('ChEMBL_ID', db.String)								
    Smiles = db.Column('Smiles', db.String)
    InCHI_key = db.Column('InCHI_key', db.String)
    RoF = db.Column('RoF', db.String)
    Molecular_Weight = db.Column('Molecular_Weight', db.String)
    LogP = db.Column('LogP', db.String)
    TPSA = db.Column('TPSA', db.String)
    HBA = db.Column('HBA', db.String)
    HBD = db.Column('HBD', db.String)
    NRB = db.Column('NRB', db.String)
    Image = db.Column('Image', db.String)
    Targets = db.Column('Targets', db.String)
