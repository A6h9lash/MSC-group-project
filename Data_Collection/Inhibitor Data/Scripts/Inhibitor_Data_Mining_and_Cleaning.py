#Import necessary packages
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

#We read our CSV file using pandas to make it a dataframe object.
df = pd.read_csv('PKIDB.csv', header=0, encoding = 'unicode_escape')

#We take the values under the INN_Name and Targets column and place them into a new dataframe.
INN = df.INN_Name
TARGETS = df.Targets
df1 = pd.DataFrame({'INN_Name': INN, 'Targets': TARGETS})

#We then re-format our new dataframe so that all of our Kinase targets are split and placed into their own separate rows.
df1 = \
(df1.set_index(df1.columns.drop('Targets',2).tolist()) #set the dataframe index to our Targets column as a list and drop it
   .Targets.str.split('\n', expand=True) #we then separate the contents of the Targets column by each new line (i.e. each kinase)
   .stack() #we then stack the dataframe from columns to index
   .reset_index() #reset our index
   .rename(columns={0:'Targets'}) #then we rename our index column back to 'Targets'
   .loc[:, df1.columns] #we then rematch the INN_Names to out new Targets column to get the final basis for our newly formatted 
                        # dataframe
)

#We remove all of the column from our first dataframe so that only the remaining data from the table matches what we want
#in our database.
df = df.drop(columns=['BrandName', 'Phase', 'Applicants', 'Links', 'LigID', 'pdbID', 'Type', 'Indications', 'Targets',
                      'Kinase families', 'First_Approval', 'SC_Patent', 'Chirality', 'Synonyms', 'FDA approved', 
                      'Melting points (°C)'])

#Smiles and InChi key information for each inhibitor is something we would like in two separate columns so we split the contents
#of the Canonical_Smiles_InChiKey by a new line (seaprator between Smile and InChi info in the column) and we put it into two
#new columns.
df[['Smiles','InChi_Key']] = df.Canonical_Smiles_InChiKey.str.split("\n",expand=True,)

#This leaves a now redundant Canonical_Smiles_InChiKey column so we remove that from that dataframe.
df = df.drop(columns=['Canonical_Smiles_InChiKey'])

#We put the values in the Smiles and InChi_Key columns in variables.
SmilesList = df['Smiles'].values
InCHIList = df['InChi_Key'].values

#Apply a substitution regex to select the 'Smiles=' and 'InChiKey=' in each of those columns and replace them with blanks. 
Smiles_regex = [re.sub('(Smiles=)', '', Smile) for Smile in SmilesList]
InCHI_regex = [re.sub('(InChiKey=)', '', InCHI) for InCHI in InCHIList]

#We remove the old Smiles and InChi_Key columns
df = df.drop(columns=['Smiles', 'InChi_Key'])

#We then add the new Smiles and InChi_Key columns filled with our regex cleaned data lists.
df['Smiles'] = Smiles_regex
df['InChi_Key'] = InCHI_regex

#Now we merge our dataframe into the dataframe template and format we actually want (df1)
df1 = pd.merge(df1,df[['INN_Name', 'RoF', 'MW', 'LogP', 'TPSA', 'HBA', 'HBD', 'NRB', 'Smiles', 'InChi_Key' ]],
               on='INN_Name', how='inner')

#To obtain the ChEMBL IDs we use BeautifulSoup to parse the html of the PKIDB website 
r = requests.get("http://www.icoa.fr/pkidb/")
soup = BeautifulSoup(r.text, 'html.parser')

#Searching for all 'tr' tags to obtain all of the table rows of the website and place them into an object
table_rows = soup.find_all('tr')

#we then specify the specific rows of the table that actually contain the data we want i.e. all but the very first one (i.e.
# the header in this case [0])
data_rows = table_rows[1:]

#Set up an empty list to collect all of the Inhibitor Names and their corresponding ChEMBL IDs.
Name_and_ChEMBLIDs = []

for row in data_rows: #for each row in our table rows containing data
    Name = row.find('td').text #extract the text of the table table data tag (Inhibitor name) and put it into a variable.
    ChEMBL = row.find_all('a')[1] #extract the 2nd 'a' tag in the data (ChEMBL link) and put it into a variable
    ChEMBL = str(ChEMBL) #convert it into a string
    ChEMBL_regex = re.search(r"(CHEMBL\d+)",ChEMBL) #use a regex to search for just the ChEMBL ID from the whole url.
    if ChEMBL_regex is not None: #if the regex finds a match
        ChEMBL_regex = ChEMBL_regex.group(0) #extract the match value
    else:
        continue 
        
    Name_and_ChEMBLIDs.append((Name, ChEMBL_regex)) #then append both the name and the ID into our empty list.

#We then create a new dataframe with the Inhibitor Names and their corresponding ChEMBL IDs 
ChEMBL_ID = pd.DataFrame(Name_and_ChEMBLIDs, columns=['INN_Name', 'ChEMBL_ID'])

#We then merge this dataframe with the dataframe containing the majority of our data.
df1 = pd.merge(df1,chembl_id[['INN_Name', 'ChEMBL_ID']],
               on='INN_Name', how='inner')

#Create an empty list to contain all of our Inhibitor structure image links
image_list = []

for Name in df1['INN_Name']: #for each Inhibitor under the INN_Name column of our main dataframe
    image_link = "http://www.icoa.fr/pkidb/static/img/mol/"+Name+".svg" #create the image link by inserting the inhibitor name
                                                                        #into a url template
    image_list.append(image_link) #then apend that image link into our list

#Then we simply create an image link new column in our dataframe with the contents of the column being our list of image links     
df1["image_link"] = image_list 

#Finally, we insert another column to act as our ID column so that we have a primary key for our inhibtor table for our database
df1.insert(0, 'INHIBITOR_ID', range(1, 1 + len(df1)))

#Writing our final dataframe into a CSV file
df1.to_csv('Inhibitor_Table.csv')