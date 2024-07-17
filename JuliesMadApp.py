# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 16:12:13 2023

@author: Nicolai.Bloch.Jessen
"""


import pandas as pd
import streamlit as st
import numpy as np
import io
import xlsxwriter

## Initial values
chosen_conditions_selectbox = ""
chosen_conditions_value_selectbox = ""


# Make a function to clear choices in streamlit, and set them to a default value
def clear_form():
    for key in st.session_state.keys():
        del st.session_state[key]
        if key == "chosen_conditions" or key == "chosen_conditions_value":
            st.session_state[key] = ""
    # Add condition
    #chosen_conditions.loc[len(chosen_conditions)] = [chosen_conditions_selectbox, chosen_conditions_value_selectbox]
    
    # Defalut choices (none)
    chosen_conditions_selectbox = ""
    chosen_conditions_value_selectbox = ""
    st.session_state.chosen_conditions_selectbox = ""
    st.session_state.chosen_conditions_value_selectbox = ""




## Read data
all_data_original = pd.read_excel("opskrifter.xlsx")
first_dish_column_number = 5
first_ingredient_row_number = 8
## Add kcal pr. person
all_data_original.loc[len(all_data_original)] = np.repeat(np.nan,len(all_data_original.columns))
all_data_original["Betingelse"][len(all_data_original)-1] = "Sum af kcal pr. person"
for dish in range(len(all_data_original.columns) - first_dish_column_number):
    all_data_original.iloc[(len(all_data_original)-1),(dish+first_dish_column_number)] = np.nansum(all_data_original['Kcal pr. måleenhed'][first_ingredient_row_number:(len(all_data_original)-1)] * all_data_original.iloc[first_ingredient_row_number:(len(all_data_original)-1),(dish+first_dish_column_number)]) / all_data_original.iloc[0,dish+first_dish_column_number]


## Make dataframes for conditions, dishes, possible_dishes
chosen_conditions = pd.DataFrame(columns = ["Betingelse", "Værdi", "Betingelse nr."])
#chosen_conditions_original = chosen_conditions.copy()
chosen_dishes = pd.DataFrame(columns = ["Ret", "Antal personer", "Ret nr."])
#chosen_dishes_original = chosen_dishes.copy()
grocery_list = pd.DataFrame(columns = ['Vare kategori', 'Vare', 'Måleenhed', 'Mængde', 'Retter varen bruges i'])
grocery_list_updated = grocery_list.copy()
#possible_dishes = list(all_data.columns[5:])
#all_data = all_data_original.copy()
grocery_list_exists1 = False


############### START APP FROM HERE! #################

#def JuliesMadApp(all_data, chosen_conditions, chosen_dishes, first_dish_column_number):
def JuliesMadApp():
    

    #global all_data, grocery_list, grocery_list_updated, grocery_list_exists
    all_data = all_data_original
    grocery_list_updated = grocery_list
    grocery_list_exists = grocery_list_exists1
    
    ## setting states, so the default values does not change
    #for k in st.session_state.keys():
    #    st.session_state[k] = st.session_state[k]
    
    
    ## Add conditions (and adjust dishes to the ones satisfying the conditions)
    chosen_conditions_selectbox = st.sidebar.selectbox(label = 'Betingelser', options = ["Maks forberedelsestid (minutter)", "Maks kcal per person"], key = "chosen_conditions")
    chosen_conditions_value_selectbox = st.sidebar.number_input('Værdi for betingelse',min_value = 0, max_value = 100000, value = 60, step = 1, key = "chosen_conditions_value")
    
    ## Add conditions
    if st.sidebar.button(label="Tilføj betingelse"):
        chosen_conditions.loc[len(chosen_conditions)] = [chosen_conditions_selectbox, chosen_conditions_value_selectbox, (len(chosen_conditions)+1)]
    
        
    ## Remove conditions
    #if "chosen_conditions" in st.session_state:
    if len(chosen_conditions) > 0:
        remove_conditions_selectbox = st.sidebar.selectbox(label = 'Fjern betingelses nr.', options = list(chosen_conditions["Betingelse nr."]), key = "remove_conditions")
        if st.sidebar.button(label="Fjern betingelse"):
            chosen_conditions.drop([remove_conditions_selectbox-1], inplace=True)
            ## Den opdaterer ikke helt rigtigt i appen. Overvej om der skal bruges de der session.State variable?
    
        

    ## Show list of conditions:
    st.markdown('## Valgte betingelser')
    st.table(chosen_conditions)
    
    
    
    ## Subset dishes based on condition
    if "Maks forberedelsestid (minutter)" in list(chosen_conditions["Betingelse"]):
        ## Removes rows from all_data not satisfying this!
        relevant_row = list(all_data[all_data["Betingelse"] == "Forberedelsestid (minutter)"].index)[0]
        dishes_to_keep = (all_data.iloc[1,first_dish_column_number:len(all_data.columns)] < int(chosen_conditions["Værdi"][chosen_conditions["Betingelse"]=="Maks forberedelsestid (minutter)"].values)) | (all_data.iloc[1,first_dish_column_number:len(all_data.columns)].isnull())
        dishes_to_keep = list(dishes_to_keep.index[dishes_to_keep])
        
        all_data = all_data.loc[:,all_data.columns.isin(list(all_data.columns[0:first_dish_column_number]) + dishes_to_keep)]

    if "Maks kcal per person" in list(chosen_conditions["Betingelse"]):
        ## Removes rows from all_data not satisfying this!
        relevant_row = list(all_data[all_data["Betingelse"] == "Sum af kcal pr. person"].index)[0]
        dishes_to_keep = (all_data.iloc[(len(all_data)-1),first_dish_column_number:len(all_data.columns)] < int(chosen_conditions["Værdi"][chosen_conditions["Betingelse"]=="Maks kcal per person"].values)) | (all_data.iloc[(len(all_data)-1),first_dish_column_number:len(all_data.columns)].isnull())
        dishes_to_keep = list(dishes_to_keep.index[dishes_to_keep])
        
        all_data = all_data.loc[:,all_data.columns.isin(list(all_data.columns[0:first_dish_column_number]) + dishes_to_keep)]
    
        
    

    ## Add dishes to chosen_dishes
    chosen_dishes_selectbox = st.sidebar.selectbox(label = 'Retter', options = list(all_data.columns[first_dish_column_number:]), key = "chosen_dishes")
    chosen_number_of_persons_selectbox = st.sidebar.number_input('Antal personer',min_value = 0, max_value = 100, value = 2, step = 1, key = "chosen_number_of_persons")
    
    
    ## Add dish to chosen dishes
    if st.sidebar.button(label="Tilføj ret"):
        chosen_dishes.loc[len(chosen_dishes)] = [chosen_dishes_selectbox, chosen_number_of_persons_selectbox, (len(chosen_dishes)+1)]
        
    ## Remove dishes
    if len(chosen_dishes) > 0:
        remove_dishes_selectbox = st.sidebar.selectbox(label = 'Fjern ret nr.', options = list(chosen_dishes["Ret nr."]), key = "remove_dishes")
        if st.sidebar.button(label="Fjern ret"):
            chosen_dishes.drop([remove_dishes_selectbox-1], inplace=True)

    
    ## Show list of dishes:
    st.markdown('## Valgte retter')
    st.table(chosen_dishes)
    
    
# =============================================================================
# 
#  # Initialize session state for the grocery list if it doesn't exist
#     if 'grocery_list_updated' not in st.session_state:
#         st.session_state.grocery_list_updated = pd.DataFrame(columns=['Vare kategori', 'Vare', 'Måleenhed', 'Mængde', 'Retter varen bruges i', 'Vare nr.'])
# 
#     grocery_list_updated = st.session_state.grocery_list_updated
# 
#     if len(chosen_dishes) > 0 and 'chosen_dishes_processed' not in st.session_state:
#         all_data_from_chosen_dishes = all_data[all_data.columns.intersection(list(all_data.columns[0:first_dish_column_number]) + list(chosen_dishes["Ret"]))]
#         all_data_from_chosen_dishes["Mængde"] = np.nan
#         all_data_from_chosen_dishes["Retter varen bruges i"] = np.nan
# 
#         ## Sum by row and list dishes it is used in:
#         for row_number in range(first_ingredient_row_number, len(all_data_from_chosen_dishes)-1):
#             data_to_use = all_data_from_chosen_dishes.iloc[row_number, first_dish_column_number:(len(all_data_from_chosen_dishes.columns)-2)]
#             data_to_use.dropna(inplace=True)
# 
#             all_data_from_chosen_dishes.at[row_number, "Mængde"] = sum(data_to_use)
#             all_data_from_chosen_dishes.at[row_number, "Retter varen bruges i"] = ', '.join(data_to_use.index.tolist())
# 
#         all_data_from_chosen_dishes = all_data_from_chosen_dishes.iloc[first_ingredient_row_number:(len(all_data_from_chosen_dishes)-1), :]
#         all_data_from_chosen_dishes = all_data_from_chosen_dishes[all_data_from_chosen_dishes["Mængde"] != 0]
# 
#         grocery_list_updated = grocery_list_updated.append(all_data_from_chosen_dishes[['Vare kategori', 'Vare', 'Måleenhed', 'Mængde', 'Retter varen bruges i']], ignore_index=True)
# 
#         grocery_list_updated["Vare nr."] = list(range(1, len(grocery_list_updated)+1))
#         st.session_state.grocery_list_updated = grocery_list_updated
#         st.session_state.chosen_dishes_processed = True
# 
#     if len(chosen_dishes) > 0:
#         ## Show grocery list
#         grocery_list_exists = True
# 
#         st.markdown('## Indkøbsseddel')
# 
#         # Assume the item name column is called something else, let's check the columns and use a correct one
#         item_name_column = 'Vare'  # Use the column for item names
# 
#         # Initialize a placeholder for displaying the updated grocery list
#         list_placeholder = st.empty()
# 
#         # Display the updated grocery list after removal
#         list_placeholder.write("Updated grocery list after removal:")
#         list_placeholder.dataframe(grocery_list_updated.drop(columns=['Vare nr.'], errors='ignore'))
# 
#         # Add checkboxes for each item in a new column 'Remove'
#         remove_flags = []
#         for index in grocery_list_updated.index:
#             remove_flags.append(st.checkbox(f'{grocery_list_updated.at[index, "Vare nr."]}: {grocery_list_updated.at[index, item_name_column]}', key=f'remove_{index}'))
# 
#         # Button to remove all selected items
#         if st.button("Fjern varer"):
#             grocery_list_updated = grocery_list_updated[[not flag for flag in remove_flags]]
#             grocery_list_updated.reset_index(drop=True, inplace=True)
#             grocery_list_updated["Vare nr."] = list(range(1, len(grocery_list_updated) + 1))
#             # Update the session state with the updated grocery list
#             st.session_state.grocery_list_updated = grocery_list_updated
#             # Update the displayed list
#             list_placeholder.dataframe(grocery_list_updated.drop(columns=['Vare nr.'], errors='ignore'))
# 
#         # Section to add other ingredients
#         st.markdown('## Add Other Ingredients')
#         new_category = st.text_input('Vare kategori')
#         new_item = st.text_input('Vare')
#         new_unit = st.text_input('Måleenhed')
#         new_quantity = st.number_input('Mængde', min_value=0.0, step=0.1)
#         new_dishes = st.text_input('Retter varen bruges i')
# 
#         if st.button("Add to List"):
#             new_row = {
#                 'Vare kategori': new_category,
#                 'Vare': new_item,
#                 'Måleenhed': new_unit,
#                 'Mængde': new_quantity,
#                 'Retter varen bruges i': new_dishes,
#                 'Vare nr.': len(grocery_list_updated) + 1
#             }
#             grocery_list_updated = grocery_list_updated.append(new_row, ignore_index=True)
#             st.session_state.grocery_list_updated = grocery_list_updated
#             list_placeholder.dataframe(grocery_list_updated.drop(columns=['Vare nr.'], errors='ignore'))
# 
#         # Convert DataFrame to Excel in memory
#         output = io.BytesIO()
#         with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#             grocery_list_updated.to_excel(writer, index=False)
#         output.seek(0)
# 
#         # Add download button
#         st.download_button(label='Download', data=output, file_name='Indkøbsseddel.xlsx')
# 
# =============================================================================
    
    
    if 'grocery_list_updated' not in st.session_state:
        st.session_state.grocery_list_updated = pd.DataFrame(columns=['Vare kategori', 'Vare', 'Måleenhed', 'Mængde', 'Retter varen bruges i', 'Vare nr.'])

    grocery_list_updated = st.session_state.grocery_list_updated

    if len(chosen_dishes) > 0 and 'chosen_dishes_processed' not in st.session_state:
        all_data_from_chosen_dishes = all_data[all_data.columns.intersection(list(all_data.columns[0:first_dish_column_number]) + list(chosen_dishes["Ret"]))]
        all_data_from_chosen_dishes["Mængde"] = np.nan
        all_data_from_chosen_dishes["Retter varen bruges i"] = np.nan

        ## Sum by row and list dishes it is used in:
        for row_number in range(first_ingredient_row_number, len(all_data_from_chosen_dishes)-1):
            data_to_use = all_data_from_chosen_dishes.iloc[row_number, first_dish_column_number:(len(all_data_from_chosen_dishes.columns)-2)]
            data_to_use.dropna(inplace=True)

            all_data_from_chosen_dishes.at[row_number, "Mængde"] = sum(data_to_use)
            all_data_from_chosen_dishes.at[row_number, "Retter varen bruges i"] = ', '.join(data_to_use.index.tolist())

        all_data_from_chosen_dishes = all_data_from_chosen_dishes.iloc[first_ingredient_row_number:(len(all_data_from_chosen_dishes)-1), :]
        all_data_from_chosen_dishes = all_data_from_chosen_dishes[all_data_from_chosen_dishes["Mængde"] != 0]

        grocery_list_updated = grocery_list_updated.append(all_data_from_chosen_dishes[['Vare kategori', 'Vare', 'Måleenhed', 'Mængde', 'Retter varen bruges i']], ignore_index=True)

        grocery_list_updated["Vare nr."] = list(range(1, len(grocery_list_updated)+1))
        st.session_state.grocery_list_updated = grocery_list_updated
        st.session_state.chosen_dishes_processed = True

    if len(chosen_dishes) > 0:
        ## Show grocery list
        grocery_list_exists = True

        st.markdown('## Indkøbsseddel')

        # Assume the item name column is called something else, let's check the columns and use a correct one
        item_name_column = 'Vare'  # Use the column for item names

        # Initialize a placeholder for displaying the updated grocery list
        list_placeholder = st.empty()

        # Display the updated grocery list after removal
        list_placeholder.write("Updated grocery list after removal:")
        list_placeholder.dataframe(grocery_list_updated.drop(columns=['Vare nr.'], errors='ignore'))

        # Section to remove ingredients
        st.markdown('## Fjern varer')
        remove_flags = []
        for index in grocery_list_updated.index:
            remove_flags.append(st.checkbox(f'{grocery_list_updated.at[index, "Vare nr."]}: {grocery_list_updated.at[index, item_name_column]}', key=f'remove_{index}'))

        # Button to remove all selected items
        if st.button("Fjern varer"):
            grocery_list_updated = grocery_list_updated[[not flag for flag in remove_flags]]
            grocery_list_updated.reset_index(drop=True, inplace=True)
            grocery_list_updated["Vare nr."] = list(range(1, len(grocery_list_updated) + 1))
            # Update the session state with the updated grocery list
            st.session_state.grocery_list_updated = grocery_list_updated
            # Update the displayed list
            list_placeholder.dataframe(grocery_list_updated.drop(columns=['Vare nr.'], errors='ignore'))

        # Section to add other ingredients
        st.markdown('## Tilføj andre varer')
        new_category = st.text_input('Vare kategori')
        new_item = st.text_input('Vare')
        new_unit = st.text_input('Måleenhed')
        new_quantity = st.number_input('Mængde', min_value=0.0, step=0.1)
        new_dishes = st.text_input('Retter varen bruges i')

        if st.button("Add to List"):
            new_row = {
                'Vare kategori': new_category,
                'Vare': new_item,
                'Måleenhed': new_unit,
                'Mængde': new_quantity,
                'Retter varen bruges i': new_dishes,
                'Vare nr.': len(grocery_list_updated) + 1
            }
            grocery_list_updated = grocery_list_updated.append(new_row, ignore_index=True)
            st.session_state.grocery_list_updated = grocery_list_updated
            list_placeholder.dataframe(grocery_list_updated.drop(columns=['Vare nr.'], errors='ignore'))

        # Convert DataFrame to Excel in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            grocery_list_updated.to_excel(writer, index=False)
        output.seek(0)

        # Add download button
        st.download_button(label='Download', data=output, file_name='Indkøbsseddel.xlsx')

