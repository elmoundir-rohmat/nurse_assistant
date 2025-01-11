import pandas as pd
import openai
from dotenv import load_dotenv
import os
import streamlit as st

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration de l'API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')  # Charger la clé depuis .env

# Charger les données
df_soins = pd.read_csv('soins.csv')
df_regles_metier = pd.read_csv('regles_metier.csv')
df_patients = pd.read_csv('patients.csv')

def extraire_interventions(texte):
    """
    Utilise l'API OpenAI pour extraire les interventions mentionnées dans un paragraphe de texte.
    Retourne une liste de codes d'intervention valides.
    """
    # Liste des codes valides pour guider OpenAI
    codes_valides = df_soins['code_intervention'].tolist()

    # Format du message pour l'API de chat
    messages = [
        {"role": "system", "content": f"""
        Tu es un assistant d'infirmiers qui aide à identifier les interventions d'infirmierie dans un texte. 
        Tu dois répondre uniquement avec les codes d'intervention valides suivants : {', '.join(codes_valides)}. 
        Si tu n'es pas certain à 100% de l'intervention décrite dans le texte, réponds uniquement par 'Je ne sais pas'. 
        Ne devine pas et ne réponds pas avec des codes incorrects.
        Voici des exemples :
        - Texte : 'Toilette complète d'un patient alité avec changement de literie' → Réponse : 'INT-0001'
        - Texte : 'Surveillance des constantes vitales' → Réponse : 'INT-0003'
        - Texte : 'Intervention non reconnue' → Réponse : 'Je ne sais pas'
    """},
        {"role": "user", "content": f"""Extrais le ou les codes d'interventions qui correspondent aux soins mentionnés dans le texte suivant : '{texte}'. Réponds uniquement avec une liste de codes valides, séparés par des virgules, ou 'Je ne sais pas' si tu n'es pas certain. Si tu identifies une seule intervention, tu mentionne seuleemnt cette intervention, si tu en as identifié plusieurs dans le même texte, tu les listes une par une. voici la base de données
         code_intervention, description, prix
        INT-0001,Toilette complète d'un patient alité avec changement de literie,50.22
        INT-0002,Aide à la mobilisation d'un patient en fauteuil roulant,124.64
        INT-0003,"Surveillance des constantes vitales (température, pouls, tension artérielle, saturation en oxygène)",124.52
        INT-0004,Administration d'un médicament par voie orale selon prescription médicale,49.71
        INT-0005,Injection intramusculaire d'un vaccin,18.55
        INT-0006,Perfusion intraveineuse de soluté salin,192.19
        INT-0007,Nettoyage et pansement d'une plaie chirurgicale,192.12
        INT-0008,Changement de pansement pour une escarre de stade II,111.06
        INT-0009,Retrait d'agrafes ou de fils de suture,97.04
        INT-0010,Surveillance de la glycémie capillaire et ajustement de l'insuline selon protocole,196.78
        INT-0011,Éducation thérapeutique pour un patient sous anticoagulants,33.26
        INT-0012,Surveillance d'un patient sous oxygénothérapie,176.49
        INT-0013,Pose d'une sonde urinaire à demeure,172.74
        INT-0014,Aspiration des voies respiratoires chez un patient trachéotomisé,145.48
        INT-0015,Prélèvement sanguin pour analyse biologique,81.08
        INT-0016,Pose d'une voie veineuse périphérique,32.49
        INT-0017,Surveillance d'un patient sous chimiothérapie,69.97
        INT-0018,Administration d'une chimiothérapie par voie intraveineuse,75.26
        INT-0019,Suivi d'un patient sous dialyse péritonéale,53.0
        INT-0020,Éducation à l'auto-surveillance glycémique pour un patient diabétique,100.77
        INT-0021,Pansement stérile pour une brûlure au deuxième degré,45.36
        INT-0022,Surveillance d'un patient sous ventilation mécanique,39.94
        INT-0023,Administration d'une antibiothérapie par voie intraveineuse,139.22
        INT-0024,Pose d'un cathéter central,77.28
        INT-0025,Suivi d'un patient sous nutrition parentérale,141.64
        INT-0026,Éducation à l'utilisation d'un inhalateur pour un patient asthmatique,98.6
        INT-0027,Pansement pour une plaie infectée,66.96
        INT-0028,Surveillance d'un patient sous sédation,115.58
        INT-0029,Administration d'une transfusion sanguine,57.17
        INT-0030,Pose d'un dispositif de compression pneumatique intermittente,137.3"""}

    ]

    # Appel à l'API OpenAI
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # Utilisez un modèle valide (par exemple, "gpt-4" ou "gpt-3.5-turbo")
        messages=messages,
        # max_tokens=50,
        # temperature=0.5
    )

    # Extraction des codes suggérés
    codes_suggeres = response.choices[0].message.content.strip()
    st.write(f"Codes suggérés par OpenAI : {codes_suggeres}")  # Log pour débogage
    return codes_suggeres.split(", ")  # Retourne une liste de codes


def mapper_code_intervention(code_suggere):
    """
    Vérifie si le code suggéré existe dans la liste des soins.
    """
    # Normalisation du code suggéré
    code_suggere = code_suggere.strip().upper()  # Supprime les espaces et convertit en majuscules

    if code_suggere in df_soins['code_intervention'].values:
        st.write(f"Code trouvé : {code_suggere}")  # Log pour débogage
        return code_suggere
    else:
        st.write(f"Code non trouvé : {code_suggere}")  # Log pour débogage
        return None  # Code non trouvé


def appliquer_regles_metier(codes_intervention):
    """
    Applique les règles métier pour calculer le prix total.
    Si aucune règle n'existe, additionne les prix des soins.
    """
    prix_total = 0
    codes_appliques = set()  # Pour éviter de compter deux fois le même code

    # Calculer le prix total sans règles métier
    for code in codes_intervention:
        if code not in codes_appliques:
            prix = df_soins.loc[df_soins['code_intervention'] == code, 'prix'].values[0]
            st.write(f"Prix pour {code} : {prix} euros")  # Log pour débogage
            prix_total += prix
            codes_appliques.add(code)

    # Vérifier s'il y a une règle métier pour cette combinaison de soins
    for _, regle in df_regles_metier.iterrows():
        if (regle['code_intervention_1'] in codes_intervention and
                regle['code_intervention_2'] in codes_intervention):
            st.write(
                f"Règle métier appliquée : {regle['code_intervention_1']} + {regle['code_intervention_2']} = {regle['prix_total']} euros")  # Log pour débogage
            prix_total = regle['prix_total']  # Appliquer le prix total de la règle
            break  # On applique la première règle trouvée

    return prix_total


def generer_facture(id_patient, codes_intervention):
    """
    Génère une facture pour un patient.
    """
    # Récupérer les informations du patient
    patient_info = df_patients.loc[df_patients['id_patient'] == id_patient]

    # Vérifier si l'ID du patient existe
    if patient_info.empty:
        st.write(f"Aucun patient trouvé avec l'ID {id_patient}.")
        return

    # Extraire les informations du patient
    patient = patient_info.iloc[0]

    # Calculer le prix total
    prix_total = appliquer_regles_metier(codes_intervention)

    # Afficher la facture
    st.write(f"Facture pour {patient['prenom']} {patient['nom']} (ID: {id_patient})")
    st.write("Soins prodigués :")
    for code in codes_intervention:
        soin = df_soins.loc[df_soins['code_intervention'] == code].iloc[0]
        st.write(f"- {soin['description']} ({code}) : {soin['prix']} euros")
    st.write(f"Prix total : {prix_total} euros")


def assistant_facturation(texte, id_patient):
    """
    Assistant Facturation : Interprète un paragraphe de texte, extrait les interventions,
    mappe les codes, applique les règles métier et génère une facture.
    """
    # Extraire les interventions du texte
    codes_suggeres = extraire_interventions(texte)
    st.write(f"Codes suggérés : {codes_suggeres}")  # Afficher dans Streamlit

    # Mapper les codes suggérés aux codes valides
    codes_intervention = []
    for code in codes_suggeres:
        code_valide = mapper_code_intervention(code)
        if code_valide:
            codes_intervention.append(code_valide)

    st.write(f"Codes valides mappés : {codes_intervention}")  # Afficher dans Streamlit

    # Générer la facture
    if codes_intervention:
        generer_facture(id_patient, codes_intervention)
        return f"Facture générée pour le patient {id_patient}"  # Retourner un message de succès
    else:
        st.warning("Aucun code valide trouvé pour générer une facture.")
        return "Aucune facture générée"  # Retourner un message d'échec


# Exemple de texte entré par l'infirmier
texte = "J'ai nettoyé et pansé une plaie chirurgicale, puis j'ai changé le pansement d'une escarre de stade II."

# ID du patient
id_patient = 8190

# Appel de l'assistant Facturation
assistant_facturation(texte, id_patient)