#Load in necessary packages
import pandas as pd
import numpy as np
import re

#Open both of our raw data files in pandas and converting them into panda dataframes
df = pd.read_csv('Kinase_Substrate_Dataset.csv')

#Filtering the dataframe for values where both Kinase and Substrate organisms are both human and checking to make sure this has
#been done
df = df[(df.KIN_ORGANISM=='human') & (df.SUB_ORGANISM=='human')]

#Remove columns in the df that aren't useful to us by their heading name and checking to make sure this has been done.
df = df.drop(['GENE','KIN_ORGANISM', 'SUB_GENE_ID', 'SUB_ORGANISM', 'SITE_GRP_ID', 'DOMAIN', 'IN_VIVO_RXN', 'IN_VITRO_RXN', 
              'CST_CAT#'],axis=1)

#Renaming columns of the dataframe for more clarity and to meet syntax requirements for SQLite and SQLAlchemy.
df = df.rename(index=str, columns = {'KINASE': 'KINASE_GENE_NAME', 'KIN_ACC_ID': 'KIN_UNIPROT_ID', 'SUBSTRATE': 'SUBSTRATE_NAME',
                                     'SUB_ACC_ID': 'SUB_UNIPROT_ID', 'SUB_GENE': 'SUB_GENE_NAME', 'SITE_+/-7_AA': 'SITE_7_AA'}) 

#Putting the Amino acid sequence information into an object
AA_Sequences = df['SITE_7_AA'].values

#Make a function which takes a string and capitalizes the 8th character in a string and makes all of the other characters in
#lower case.
def capitalize_8th(string):
    return string[:7].lower() + string[7:].capitalize()

#Set up an empty list to collect all of the cleaned sequences
CleanedSequences = []

#Running a for loop to clean the amino acid sequences
for sequence in AA_Sequences: #for every sequence in the amino acid sequence
    sequence = str(sequence) #convert the sequence into a string
    sequence = capitalize_8th(sequence) #pass the string through our created function 
    sequence = sequence.swapcase() #swap the cases of the strings to the opposite i.e. all lowercase characters become uppercase
                                   #and vice versa
    CleanedSequences.append(sequence) #append the edited sequence to the empty list

#Dropping the old amino acid sequence column in the dataframe
df = df.drop(columns=['SITE_7_AA'])

#Inserting the new column with the cleaned data
df.insert(6, 'SITE_7_AA', CleanedSequences)

#Load in the Phosphorylation_site_dataset into pandas and check to make sure it has loaded in properly.
df1 = pd.read_csv('Phosphorylation_site_dataset.csv')

#Similar to the Kinase_substrate_dataset we see that there is data on organisms that aren't human. So we filter the dataframe 
#in the same way to only have rows where the organism is human and check to make sure this has been done.
df1 = df1[df1.ORGANISM == 'human']

#Dropping all columns in the Phosphorylation_site_dataset except ACC_ID and HU_CHR_LOC

df1 = df1.drop(columns=['GENE','PROTEIN', 'MOD_RSD', 'SITE_GRP_ID','ORGANISM', 'MW_kD', 'DOMAIN', 'SITE_+/-7_AA', 'LT_LIT',
                        'MS_LIT', 'MS_CST', 'CST_CAT#'])

#We re-name the ACC_ID column to match our other dataset in order to actually carry out the next merge step.
df1 = df1.rename(index=str, columns = {'ACC_ID': 'SUB_UNIPROT_ID', 'HU_CHR_LOC': 'CHR_LOC'}) 

#Dropping duplicates in Dataframe1.
df1 = df1.drop_duplicates(keep = 'first', inplace=False)

#Now that the rows are reduced, we merge the dataframes together by the SUB_UNIPROT_ID so that Human Chromosome Location is now
#included to our cleaned table.
df = pd.merge(df,df1[['SUB_UNIPROT_ID','CHR_LOC']],on='SUB_UNIPROT_ID', how='inner')

#We drop all of our columns except for SUB_UNIPROT_ID and SUB_GENE_NAME and place it into another dataframe object then we can 
#drop any duplicates reducing the number of rows from 10981 rows and 2531 rows.
df2 = df.drop(columns=['KINASE_GENE_NAME','KIN_UNIPROT_ID', 'SUBSTRATE_NAME', 'SUB_MOD_RSD','SITE_7_AA', 'CHR_LOC'])
df2 = df2.drop_duplicates(keep = 'first', inplace=False)

#Now we put all of our UniProt IDs into another object in order to feed through the UniProt API.
UniProt_IDs = df2['SUB_UNIPROT_ID'].values

#Create an empty list to contain all of our UniProt Entries.
EntryList = []

for ID in UniProt_IDs: #for every ID in our object containing all of our UniProt IDs
    ID = str(ID) #convert the ID into a string
    ID = re.sub('([-,_].*)$', '', ID) #apply a regex to clean ID string in categories 1 and 2.
    try: #pass cleaned IDs through UniProt API to get a table containing ID and corresponding UniProt Entry name read by pandas                              
        data = pd.read_csv("https://www.uniprot.org/uniprot/?query="+ID+"&sort=score&columns=id,entry%20name&format=tab", 
                           sep="\t") 
        entry = data["Entry name"][0] #we then store the first value in the Entry name column of the table as this corresponds
                                      #to our specific ID.
        EntryList.append(entry) #We then append that entry name into our empty list
    except:
        EntryList.append('-') #In the case, of IDs in category 3 we would just append a '-' to represent a blank.

#Now we insert our list of UniProt entries to our second dataframe...
df2.insert(0, 'SUB_ENTRY_NAME', EntryList)

#...and merge it with our original dataframe so that UniProt Entries are included.
df = pd.merge(df,df2[['SUB_UNIPROT_ID','SUB_ENTRY_NAME']],on='SUB_UNIPROT_ID', how='inner')

#Finally, we insert a a PHOSPHO_ID column into our dataframe 
df.insert(0, 'PHOSPHO_ID', range(1, 1 + len(df)))

#Writing our final dataframe into a CSV file
df.to_csv('Phosphosite_Table.csv')