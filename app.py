import streamlit as st
import pandas as pd
from main import extraire_interventions, mapper_code_intervention, appliquer_regles_metier, generer_facture, \
    assistant_facturation


st.title("Assistant de Facturation Médicale")

df_soins = pd.read_csv('soins.csv')
df_regles_metier = pd.read_csv('regles_metier.csv')
df_patients = pd.read_csv('patients.csv')


texte = st.text_area("Entrez le texte décrivant les interventions médicales :")

id_patient = st.number_input("Entrez l'ID du patient :", min_value=1, step=1)

if st.button("Générer la facture"):
    if texte and id_patient:
        result = assistant_facturation(texte, id_patient)

        st.write("### Résultat de la facturation :")
        st.write(result)
    else:
        st.error("Veuillez remplir tous les champs.")