import streamlit as st
from stmol import showmol
import py3Dmol
import requests
import biotite.structure.io as bsio
import numpy as np

# Set up the sidebar with title and description
st.sidebar.title('Protein Prediction')

# Function to render the molecular structure
def render_mol(pdb):
    pdbview = py3Dmol.view()
    pdbview.addModel(pdb, 'pdb')
    pdbview.setStyle({'cartoon': {'color': 'spectrum'}})
    pdbview.setBackgroundColor('white')
    pdbview.zoomTo()
    pdbview.zoom(2, 800)
    pdbview.spin(True)
    showmol(pdbview, height=500, width=800)


# Default protein sequence
DEFAULT_SEQ = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
txt = st.sidebar.text_area('Input sequence', DEFAULT_SEQ, height=275)


# Function to call the ESMFold API and update the display
def update(sequence=txt):
    try:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence,
                                 verify=False)  # Setting verify to False for SSL issue
        response.raise_for_status()  # Raise an error for bad status codes

        pdb_string = response.content.decode('utf-8')

        with open('predicted.pdb', 'w') as f:
            f.write(pdb_string)

        struct = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
        b_value = round(struct.b_factor.mean(), 4)

        # Display the predicted structure
        st.subheader('Visualization of predicted protein structure')
        render_mol(pdb_string)

        # Display the plDDT value
        st.subheader('plDDT')
        st.write('plDDT is a per-residue estimate of the confidence in prediction on a scale from 0-100.')
        st.info(f'plDDT: {b_value}')

        # Provide a download button for the PDB file
        st.download_button(
            label="Download PDB",
            data=pdb_string,
            file_name='predicted.pdb',
            mime='text/plain',
        )
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")


# Function to fetch predicted structure by ID
def fetch_predicted_structure(protein_id):
    try:
        url = f"https://api.esmatlas.com/fetchPredictedStructure/{protein_id}"
        response = requests.get(url, verify=False)  # Setting verify to False for SSL issue
        response.raise_for_status()

        pdb_string = response.content.decode('utf-8')

        with open('predicted_by_id.pdb', 'w') as f:
            f.write(pdb_string)

        # Display the predicted structure
        st.subheader(f'Visualization of predicted protein structure for {protein_id}')
        render_mol(pdb_string)

        # Provide a download button for the PDB file
        st.download_button(
            label="Download PDB",
            data=pdb_string,
            file_name=f'{protein_id}.pdb',
            mime='text/plain',
        )
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")


# Function to fetch confidence prediction by ID
def fetch_confidence_prediction(protein_id):
    try:
        url = f"https://api.esmatlas.com/fetchConfidencePrediction/{protein_id}"
        response = requests.get(url, verify=False)  # Setting verify to False for SSL issue
        response.raise_for_status()

        confidence_data = response.json()

        st.subheader(f'Confidence Prediction for {protein_id}')
        st.json(confidence_data)
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")


# Function to fetch sequence by ID
def fetch_sequence(protein_id):
    try:
        url = f"https://api.esmatlas.com/fetchSequence/{protein_id}"
        response = requests.get(url, verify=False)  # Setting verify to False for SSL issue
        response.raise_for_status()

        sequence_data = response.json()

        st.subheader(f'Sequence for {protein_id}')
        st.json(sequence_data)
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")


# Function to fetch sequence embedding by ID (JSON format)
def fetch_embedding_json(protein_id):
    try:
        url = f"https://api.esmatlas.com/fetchEmbedding/ESM2/{protein_id}.json"
        response = requests.get(url, verify=False)  # Setting verify to False for SSL issue
        response.raise_for_status()

        embedding_data = response.json()

        st.subheader(f'Embedding (JSON) for {protein_id}')
        st.json(embedding_data)
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")


# Function to fetch sequence embedding by ID (binary format)
def fetch_embedding_bin(protein_id):
    try:
        url = f"https://api.esmatlas.com/fetchEmbedding/ESM2/{protein_id}.bin"
        headers = {"Accept": "application/octet-stream"}
        response = requests.get(url, headers=headers, verify=False)  # Setting verify to False for SSL issue
        response.raise_for_status()

        array = np.frombuffer(response.content, dtype=np.float16)

        st.subheader(f'Embedding (Binary) for {protein_id}')
        st.write(array)
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")


# Sidebar inputs for fetching data by ID
st.sidebar.subheader("Fetch Data by MGnify Protein ID")
protein_id = st.sidebar.text_input('Protein ID (starts with MGYP)')

# Buttons for fetching different types of data
if st.sidebar.button('Fetch Predicted Structure'):
    fetch_predicted_structure(protein_id)

if st.sidebar.button('Fetch Confidence Prediction'):
    fetch_confidence_prediction(protein_id)

if st.sidebar.button('Fetch Sequence'):
    fetch_sequence(protein_id)

if st.sidebar.button('Fetch Embedding (JSON)'):
    fetch_embedding_json(protein_id)

if st.sidebar.button('Fetch Embedding (Binary)'):
    fetch_embedding_bin(protein_id)

# Create the Predict button in the sidebar
predict = st.sidebar.button('Predict', on_click=update)

# Show a warning message if the Predict button has not been clicked
if not predict:
    st.warning('👈 Enter protein sequence data!')
