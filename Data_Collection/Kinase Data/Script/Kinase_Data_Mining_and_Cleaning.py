#Import necessary packages
import pandas as pd
import re

#Using the read_html function of pandas to obtain a list of dataframes of any tables on the KinHub page.
dfs = pd.read_html('http://www.kinhub.org/kinases.html', header=0)

#Taking the first (and only) dataframe from the list and putting it into it's own object.
df = dfs[0]

#We remove the columns from the dataframe that aren't particularly needed for us.
df = df.drop(columns=['Manning Name','HGNC Name'])

#Renaming the columns to be better suited for SQLite syntax for the database as well as for clarity.
df = df.rename(index=str, columns={'xName': 'Kinase_Gene_Name','Kinase Name': 'Kinase_Protein_Name', 'Group': 'Kinase_Group'})

#Place all of the Uniprot IDs into an object.
UniProt_IDs = df['UniprotID'].values

#Set up an empty list to contain all of our Uniprot entries.
UniProtEntry = []

for ID in UniProt_IDs: #for each ID in the Uniprot ID list
    ID = str(ID) #convert the ID into a string
    #Put each ID string into the Uniprot API to produce a table containing the ID and corresponding Entry Name.
    data = pd.read_csv("https://www.uniprot.org/uniprot/?query="+ID+"&sort=score&columns=id,entry%20name&format=tab", sep="\t")
    entry = data["Entry name"][0] #Place the first result in the Entry name column (the one we're interested in) into an object
    UniProtEntry.append(entry) #Append the entry name into our empty list.

#Insert a column into our dataframe containing our list of Uniprot Entry names.
df['UniProt_Entry'] = UniProtEntry

#Same use of pandas read_html function to take all tables on specified page into a list of dataframes
dfs1 = pd.read_html('http://kinase.com/web/current/kinbase/genes/SpeciesID/9606/', header=0)

#Taking the first (and only) dataframe from the list and putting it into it's own object.
df1 = dfs1[0]

#Remove all of the columns in the dataframe except for Kinase Gene and Alias
df1 = df1.drop(columns=['Select','Species','Classification'])

#Renaming the Kinase Gene column to be the exact same as the one in our main dataframe in order for the next merge step to work
df1 = df1.rename(index=str, columns={"Gene": "Kinase_Gene_Name"})

#Merging the two dataframes so that Alias is now a part of our main Kinase table.
df = pd.merge(df,df1[['Kinase_Gene_Name','Alias']],on='Kinase_Gene_Name', how='inner')

#Take all of the values under the UniprotID and put them into a separate object.
UniProt_IDs = df['UniprotID'].values

#Create an empty list for our corresponding subcellular locations to be collected into. 
LocationList = []

for ID in UniProt_IDs: #for each ID in our list of Uniprot IDs
    ID = str(ID) #convert them into a string
    data = pd.read_csv("http://www.uniprot.org/uniprot/?query="+ID+"&sort=score&columns=id,comment(SUBCELLULAR%20LOCATION)&format=tab",
                       sep="\t") #insert each ID into the Uniprot API to output a table containing our ID and its corresponding
                                 #subcellular location.
    location = data["Subcellular location [CC]"][0] #take the first result of the subcellular location column of the table and
                                                    #put it into another object. First location is the one we want.
    LocationList.append(location) #append this location into our empty list.

df['Subcellular_Location'] = LocationList #We then make another column in our dataframe with the contents of our filled list.

#Taking all of the values in the subcellular location column and put it into an object.
CellLocations = df['Subcellular_Location'].values

#Create an empty list to contain our cellular locations.
LocationList = []

for Location in CellLocations: #for each location in our locations object
    Location = str(Location) #we convert the location into a string
    Location = Location.replace('SUBCELLULAR LOCATION: ', '') #replace the 'SUBCELLULAR LOCATION:' part of each location
                                                              #description with an empty space. Therefore, removing it.
    LocationList.append(Location) #then append the slightly cleaner version of the list into our empty list.

#We run this first regex on our Location List to remove any references in '{}' with contents between 10-30 characters, to remove
#the smallest bracketed references.
Regex1 = [re.sub('{.{10,30}}', '', item) for item in LocationList]

#We then run another regex to remove '{}' references with contents between 50-100 characters, to remove slight bigger references.
Regex2 = [re.sub('{.{50,100}}', '', item) for item in Regex1]

#Then we remove '{}' reference with contents between 100-200 characters.
Regex3 = [re.sub('{.{100,200}}', '', item) for item in Regex2]

#Then 200-400 characters...
Regex4 = [re.sub('{.{200,400}}', '', item) for item in Regex3]

#Finally, all the remaining '{}' references are removed.
Regex5 = [re.sub('{.*}', '', item) for item in Regex4]

#We use a regex to remove all Notes up to the first ';'. This works properly in all case except 3 with sentences starting with
#'targeted', 'isoform 2', 'cytoplasmic' not being completely removed.
Regex6 = [re.sub('\sNote.*?[;]', '', item) for item in Regex5]

#We then use this regex to remove all Notes ending in '.'
Regex7 = [re.sub('\sNote.*[.]', '', item) for item in Regex6]

#These next three regexs are used to remove the three missed exceptions left from Regex6.
Regex8 = [re.sub('\stargeted.*[.]', '', item) for item in Regex7]
Regex9 = [re.sub('\sisoform.*[;]', '', item) for item in Regex8]
Regex10 = [re.sub('\scytoplasmic.*?[;]', '', item) for item in Regex9]

#Finally, we remove any and all '[]' in our location list.
Regex11 = [re.sub('[[]', '', item) for item in Regex10]
Regex12 = [re.sub('[]]', '', item) for item in Regex11]

#Removing the old Subcellular Location column from our dataframe.
df = df.drop(columns=['Subcellular_Location'])

#Re-adding the column with it's content being our fully regex'ed list of locations.
df['Subcellular Location'] = Regex12

#Writing our final dataframe into a CSV file
df.to_csv('Kinase_Table.csv')