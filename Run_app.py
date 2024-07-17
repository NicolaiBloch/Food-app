# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 16:29:13 2023

@author: Nicolai.Bloch.Jessen
"""



from JuliesMadApp import JuliesMadApp

import pandas as pd
import streamlit as st
import numpy as np

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
#possible_dishes = list(all_data.columns[5:])
all_data = all_data_original.copy()
grocery_list_exists = False



#JuliesMadApp(all_data, chosen_conditions, chosen_dishes, first_dish_column_number)
JuliesMadApp()