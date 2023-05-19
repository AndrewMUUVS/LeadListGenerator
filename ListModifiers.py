import pandas as pd
import numpy as np
import openai
import time



def improve_quality(df):

    # Reordering the columns
    columns = ['CAMPAIGN_ID_ARRAY__C', 'COMPANY', 'CITY', 'COUNTRY__C', 'EMAIL', 'FIRSTNAME', 'LASTNAME', 'LEADSOURCE', 
               'LINKEDIN_PROFILE__C', 'MOBILEPHONE', 'OFFICE_PHONE__C', 'PHONE', 'RATING', 'REGION__C', 'TITLE', 
               'WEBSITE', 'NOTE', 'MESSAGE', 'EXISTING_ACCOUNT__C']

    improved = df.reindex(columns=columns)

    # Setting np.nan for later analyses
    improved = improved.replace('', np.nan)
    
    # Setting Note column as empty string to use "+" later
    improved['NOTE'] = ''

    return improved

def form_zoominfo(zo, campaign):

    # Dropping columns that aren't needed
    required_cols = ['profileUrl', 'firstName', 'lastName', 'title', 'Email Address', 'Mobile phone','Contact Accuracy Score', 'Country', 'Website', 'Company Name', 'Within EU']
    zo = zo[required_cols].dropna(how='all', axis=1)

    # Rename the columns
    zo = zo.rename(columns={'profileUrl':'LINKEDIN_PROFILE__C', 'firstName':'FIRSTNAME', 'lastName':'LASTNAME', 
                            'title':'TITLE', 'Email Address':'EMAIL','Mobile phone':'MOBILEPHONE', 
                            'Contact Accuracy Score':'RATING', 'Country':'COUNTRY__C', 
                            'Website':'WEBSITE', 'Company Name':'COMPANY','Within EU':'REGION__C'})

    # Adding columns
    new_cols = {'CAMPAIGN_ID_ARRAY__C':campaign,'CITY': np.nan,'PHONE':np.nan,'OFFICE_PHONE__C':np.nan,'EXISTING_ACCOUNT__C':np.nan,'LEADSOURCE':'demand_gen','MESSAGE':np.nan,'NOTE':np.nan}
    zo = zo.assign(**new_cols)

    # Reordering the columns and clean the data
    zo = improve_quality(zo)

    return zo


def form_cognism(co, campaign):

    # Dropping columns that aren't needed
    required_cols = ['profileUrl','First Name', 'Last Name', 'Matched Job Title', 'Cognism Email', 'Direct', 'Mobile', 'Office', 'Person Country', 'Matched Web Site', 'Company Name Input']
    co = co[required_cols].dropna(how='all', axis=1)

    # Rename the columns
    co = co.rename(columns={'profileUrl':'LINKEDIN_PROFILE__C', 'First Name':'FIRSTNAME', 
                            'Last Name':'LASTNAME','Matched Job Title':'TITLE', 'Cognism Email':'EMAIL',
                            'Direct':'PHONE', 'Mobile':'MOBILEPHONE', 'Office':'OFFICE_PHONE__C',
                            'Person Country':'COUNTRY__C', 'Matched Web Site':'WEBSITE', 
                            'Company Name Input':'COMPANY'})

    # Adding columns
    new_cols = {'CAMPAIGN_ID_ARRAY__C':campaign,'CITY': np.nan,'REGION__C':np.nan,'RATING':np.nan,'EXISTING_ACCOUNT__C':np.nan,'LEADSOURCE':'demand_gen','MESSAGE':np.nan,'NOTE':np.nan}
    co = co.assign(**new_cols)

    # Improving quality of the cognism data
    co['PHONE'] = co['PHONE'].str.replace('\t', '')
    co['MOBILEPHONE'] = co['MOBILEPHONE'].str.replace('\t', '')
    co['OFFICE_PHONE__C'] = co['OFFICE_PHONE__C'].str.replace('\t', '')

    co = co.replace(['DNC','TPS','CTPS'], np.nan)

    # Reordering the columns and clean the data
    co = improve_quality(co)

    return co

def form_phantombuster(ph, campaign):

    # Dropping columns that aren't needed
    required_cols = ['query','firstName','lastName','currentJobTitle','emailAddress','currentCompanyName','location','phoneNumber','allSkills']
    ph = ph[required_cols].dropna(how='all', axis=1)

    # Rename the columns
    ph = ph.rename(columns={'query':'LINKEDIN_PROFILE__C', 'firstName':'FIRSTNAME', 'lastName': 'LASTNAME','currentJobTitle':'TITLE', 'emailAddress':'EMAIL', 'phoneNumber':'PHONE','currentCompanyName':'COMPANY', 'website':'WEBSITE', 'location':'CITY', 'allSkills':'MESSAGE'})

    # Adding columns
    new_cols = {'CAMPAIGN_ID_ARRAY__C':campaign,'COUNTRY__C': np.nan,'LEADSOURCE':'demand_gen','MOBILEPHONE':np.nan,'OFFICE_PHONE__C':np.nan,'RATING':np.nan,'REGION__C':np.nan,'NOTE':np.nan,'EXISTING_ACCOUNT__C':np.nan}
    ph = ph.assign(**new_cols)

    # Reordering the columns and clean the data
    ph = improve_quality(ph)

    return ph


def merge(zoominfo, cognism, phantombuster, campaign):
    
    # Modifying the two dataframes
    zoominfo = form_zoominfo(zoominfo, campaign)
    cognism = form_cognism(cognism, campaign)
    phantombuster = form_phantombuster(phantombuster, campaign)
    
    # merged is cognism in the beginning
    merged = cognism.copy() 
    duplic = pd.DataFrame(columns=['LINKEDIN_PROFILE__C', 'EMAIL', 'MOBILEPHONE'])
    
    # iterating through zoominfo to put into merged
    for z_idx, z_row in zoominfo.iterrows():
        
        # Extracting important information from zoominfo row
        linkedIn = z_row["LINKEDIN_PROFILE__C"]
        withInEU = z_row["REGION__C"]
        
        # Searching for same linkedIn profile in cognism/merged
        mask = (merged['LINKEDIN_PROFILE__C'] == linkedIn)
        c_df = merged[mask]
        
        # Has no match and need to be added to merged
        if len(c_df) == 0:
            merged.loc[len(merged)] = z_row.values

            
        # Has one match and information need to be added to row
        elif len(c_df) == 1:
            c_row = c_df.iloc[0]
            
            if withInEU == True: 
                
                # Checking for duplications that might still be useful
                if (c_row['EMAIL'] != z_row['EMAIL']) and not pd.isna(c_row['EMAIL']) and not pd.isna(z_row['EMAIL']):
                    duplic.loc[len(duplic)] = [z_row['LINKEDIN_PROFILE__C'], z_row['EMAIL'], np.nan]
                    
                cognism_numbers = [c_row['MOBILEPHONE'], c_row['OFFICE_PHONE__C'], c_row['PHONE']]
                unique_number = (z_row['MOBILEPHONE'] not in cognism_numbers) and not pd.isna(z_row['MOBILEPHONE'])
                
                if unique_number:
                    if pd.isna(c_row['OFFICE_PHONE__C']): 
                        merged.loc[mask, 'OFFICE_PHONE__C'] = z_row['MOBILEPHONE']
                        
                    elif pd.isna(c_row['PHONE']): 
                        merged.loc[mask, 'PHONE'] = z_row['MOBILEPHONE']
                        
                    elif not pd.isna(c_row['MOBILEPHONE']): 
                        duplic.loc[len(duplic)] = [z_row['LINKEDIN_PROFILE__C'], np.nan, z_row['MOBILEPHONE']]

                # Take cognism value except they are nan
                for col in list(merged.columns):
                    if pd.isna(c_row[col]):
                        merged.loc[mask, col] = z_row[col]
            
            else: 
                # Checking for duplications that might still be useful
                if (c_row['EMAIL'] != z_row['EMAIL']) and not pd.isna(c_row['EMAIL']) and not pd.isna(z_row['EMAIL']):
                    duplic.loc[len(duplic)] = [c_row['LINKEDIN_PROFILE__C'], c_row['EMAIL'], np.nan]
                
                cognism_numbers = [c_row['MOBILEPHONE'], c_row['OFFICE_PHONE__C'], c_row['PHONE']]
                unique_number = (z_row['MOBILEPHONE'] not in cognism_numbers) and not pd.isna(z_row['MOBILEPHONE'])
                
                if unique_number:
                    if pd.isna(c_row['OFFICE_PHONE__C']): 
                        merged.loc[mask, 'OFFICE_PHONE__C'] = z_row['MOBILEPHONE']
                        
                    elif pd.isna(c_row['PHONE']): 
                        merged.loc[mask, 'PHONE'] = z_row['MOBILEPHONE']
                        
                    elif not pd.isna(c_row['MOBILEPHONE']): 
                        duplic.loc[len(duplic)] = [c_row['LINKEDIN_PROFILE__C'], np.nan, c_row['MOBILEPHONE']]
                
                # Take zoominfo value except they are nan
                for col in list(merged.columns):
                    if not pd.isna(z_row[col]):
                        merged.loc[mask, col] = z_row[col]
                        
        # Has more than one match so zoominfo has duplicates    
        else: print("Error: Cognism or Zoominfo has duplicates!!!")


    # Iterate through whole merged dataframe and fill in missing values from ph
    # NOT IDEAL: COMPARING IN MERGED CREATION DIRECTLY
    for idx, row in merged.iterrows():
        linkedIn = row["LINKEDIN_PROFILE__C"]
        mask = (phantombuster['LINKEDIN_PROFILE__C'] == linkedIn)
        match = phantombuster[mask]

        # Insert missing values from ph
        for col in merged.columns:
            if pd.isna(row[col]):
                merged.at[idx, col] = match[col].values[0]

        # Handling duplicate EMAILS
        if (row['EMAIL'] != match['EMAIL'].values[0]) and not pd.isna(match['EMAIL'].values[0]):
            duplic.loc[len(duplic)] = [linkedIn, match['EMAIL'].values[0], np.nan]

        # Handling duplicate NUMBERS
        merged_numbers = [row['MOBILEPHONE'], row['OFFICE_PHONE__C'], row['PHONE']]
        unique_number = (match['PHONE'].values[0] not in merged_numbers) and not pd.isna(match[col].values[0])
                
        if unique_number:
            if pd.isna(row['OFFICE_PHONE__C']): 
                merged.at[idx, 'OFFICE_PHONE__C'] = match['PHONE'].values[0]
                        
            elif pd.isna(row['PHONE']): 
                merged.at[idx, 'PHONE'] = match['PHONE'].values[0]
                        
            elif not pd.isna(c_row['MOBILEPHONE']): 
                duplic.loc[len(duplic)] = [linkedIn, np.nan, match['PHONE'].values[0]]


    # Filling the duplicates in notes 
    # NOT IDEAL: BEST TO NOT EVEN CREATE DF BUT DIRECLTY INSERT IN NOTES
    for idx, row in duplic.iterrows():
        linkedIn = row["LINKEDIN_PROFILE__C"]
        mask = (merged['LINKEDIN_PROFILE__C'] == linkedIn)
        
        if not pd.isna(duplic.at[idx,'EMAIL']): merged.loc[mask, 'NOTE'] += f"Alternative Email: {duplic.at[idx,'EMAIL']} "
        if not pd.isna(duplic.at[idx,'MOBILEPHONE']): merged.loc[mask, 'NOTE'] += f"Alternative Number: {duplic.at[idx,'MOBILEPHONE']} "

    # Improve quality
    merged = merged.replace('', np.nan)
    

    return merged


def create_email(df, openai_key):
    openai.api_key = openai_key

    count = 0
    for idx, row in df.iterrows():
    
        # Template for AI
        if not pd.isna(row['FIRSTNAME']) and not pd.isna(row['CITY']) and not pd.isna(row['TITLE']) and not pd.isna(row['MESSAGE']):
        
            # Template for AI
            comma = ","
            template = f"Hey {row['FIRSTNAME']}, I hope your day is going well in {row['CITY'].split(comma)[0]}. The reason for my message is that I noticed your experience as an {row['TITLE'].split(comma)[0]} as well as with [] and []."
    
            # create a prompt
            skills = row['MESSAGE']
            prompt = f"Extract two different techincal data analytics skills from a skillset. \
                        Prioritize SQL, dbt, Snowflake. \
                        Machine Learning, Deep Learning, C++, Java or Data Visualization should not be mentioned.\
                        Give no descriptions and list the two skills with a comma between them.\
                        The skillset: {skills}."

            # generate text using the GPT-3 language model
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=2000,
                n=1,
                stop=None,
                temperature=0.7,
            )

            # print the generated text and save it
            skills = response.choices[0].text
            skills = skills.strip()
            print()
            print("Extracted skills: ", skills)
    
            # Waiting if exceeded request limits
            count = count + 1
            if count == 60:
                count = 0
                time.sleep(70)
        
            # Fill in the template
            comma = ","
            template = f"Hey {row['FIRSTNAME']}, I hope your day is going well in {row['CITY'].split(comma)[0]}. The reason for my message is that I noticed your experience as an {row['TITLE'].split(comma)[0]} as well as with {skills.split(comma)[0]} and{skills.split(comma)[1]}."
        
            # Insert the text and print it
            df.loc[idx, 'MESSAGE'] = template
            print(idx, df.loc[idx, 'MESSAGE'])


        elif not pd.isna(row['FIRSTNAME']) and not pd.isna(row['CITY']) and not pd.isna(row['TITLE']):
            # Fill in the template
            comma = ","
            template = f"Hey {row['FIRSTNAME']}, I hope your day is going well in {row['CITY'].split(comma)[0]}. The reason for my message is that I noticed your experience as an {row['TITLE'].split(comma)[0]}."
        
            # Insert the text and print it
            df.loc[idx, 'MESSAGE'] = template
            print(idx, df.loc[idx, 'MESSAGE'])

    return df


def test():
    zoominfo = pd.read_csv("/Users/leadang/Documents/Coding/ListCreation/dbt_analytics_engineer_phase_2/Zoominfo.csv")
    cognism = pd.read_csv("/Users/leadang/Documents/Coding/ListCreation/dbt_analytics_engineer_phase_2/Cognism.csv")
    phantombuster = pd.read_csv("/Users/leadang/Documents/Coding/ListCreation/dbt_analytics_engineer_phase_2/Phantombuster.csv")

    merged = merge(zoominfo,cognism,phantombuster,'dbt_analytics_engineer_phase_2')
    merged_right = pd.read_csv("/Users/leadang/Documents/Coding/ListCreation/dbt_analytics_engineer_phase_2/Merged.csv")
    are_same = merged.equals(merged_right)

    # Print the result
    print(are_same)


def main():
    test()

if __name__ == '__main__':
    main()