import streamlit as st
import pandas as pd
from main import extraire_interventions, mapper_code_intervention, appliquer_regles_metier, generer_facture, \
    assistant_facturation

# Titre de l'application
st.title("Assistant de Facturation Médicale")

# Charger les données
df_soins = pd.read_csv('soins.csv')
df_regles_metier = pd.read_csv('regles_metier.csv')
df_patients = pd.read_csv('patients.csv')


# Saisie du texte par l'utilisateur
texte = st.text_area("Entrez le texte décrivant les interventions médicales :")

# Saisie de l'ID du patient
id_patient = st.number_input("Entrez l'ID du patient :", min_value=1, step=1)

# Bouton pour lancer l'analyse
if st.button("Générer la facture"):
    if texte and id_patient:
        # Appel de la fonction principale
        result = assistant_facturation(texte, id_patient)

        # Affichage des résultats
        st.write("### Résultat de la facturation :")
        st.write(result)
    else:
        st.error("Veuillez remplir tous les champs.")