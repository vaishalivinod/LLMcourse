# streamlit_app.py
import streamlit as st
import requests
import xml.etree.ElementTree as ET
import json
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO

HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

study_prompts = {
    "Type of Task": (
        "What type of primary motor task was performed during gait analysis "
        "(e.g., walking, dual-task walking, treadmill walking)? Report the specific task if mentioned. "
        "If not mentioned, write: 'Not Mentioned'."
    ),
    "Task Parameters": (
        "Were specific task parameters (e.g., walking speed, distance, incline) reported? "
        "List them clearly. If not mentioned, write: 'Not Mentioned'."
    ),
    "Secondary Task": (
        "Was a secondary task performed alongside walking (e.g., cognitive counting, visual tracking)? "
        "If yes, specify the task. If not mentioned, write: 'Not Mentioned'."
    ),
    "Cohort": (
        "Describe the participant cohort (e.g., healthy adults, stroke patients, Parkinson's disease). "
        "Report the group type clearly. If not mentioned, write: 'Not Mentioned'."
    ),
    "Number of Participants": (
        "How many participants were included in the EEG gait study? Look for phrases like 'N = X', 'X participants', "
        "'a total of X subjects', or 'sample size of X'. Extract the exact number (e.g., 30, 64). "
        "If not mentioned, write: 'Not Mentioned'."
    ),
    "Age": (
        "What is the age range of participants involved in the EEG gait study? "
        "Report the range (e.g., 18–65 years). If not mentioned, write: 'Not Mentioned'."
    ),
    "EEG System": (
        "Which EEG recording system or amplifier was used in this study (e.g., Biosemi, Brain Products, Neuroscan)? "
        "Report the name. If not mentioned, write: 'Not Mentioned'."
    ),
    "Sampling Rate": (
        "What was the sampling rate of the EEG data in Hz? Report the value. "
        "If not mentioned, write: 'Not Mentioned'."
    ),
    "Number of EEG Electrodes": (
        "How many EEG electrodes or channels were recorded during the study? Look for phrases such as 'X channels', "
        "'X electrodes', 'a total of X channels', 'N = X', or 'using a 32-channel cap'. Extract the exact number (e.g., 32, 64, 128). "
        "If not mentioned, write: 'Not Mentioned'."
    ),
    "Analysis Software": (
        "What software/toolbox was used for EEG data analysis (e.g., EEGLAB, FieldTrip, MNE)? "
        "Specifically mention only the toolbox and not the programming language"
        "Report the name(s). If not mentioned, write: 'Not Mentioned'."
    )
}

# Gait-Related EEG Preprocessing Prompts
gait_eeg_prompts = {
    "Bandpass Filter": (
        "Step 1: Identify if a bandpass filter was applied to the EEG data. Look for phrases like 'bandpass filtered', 'filtered between', 'passband of', or similar terms indicating a frequency range was retained.",
        "Step 2: If a bandpass filter was identified in Step 1, extract the lower and upper cutoff frequencies in Hz. Report as: 'Bandpass filter: X Hz - Y Hz'. If no bandpass filter was mentioned or identified in Step 1, write: 'Not Mentioned'."
    ),
    "High-Pass Filter": (
        "Step 1: Determine if a high-pass filter was used to remove slow signal drifts. Search for terms such as 'high-pass filter', 'HPF', or 'cutoff frequency' associated with the removal of low-frequency components.",
        "Step 2: If a high-pass filter was identified in Step 1, extract the cutoff frequency value and its unit (which should be Hz). Report as: 'High-pass filter: X Hz'. If no high-pass filter was mentioned or identified in Step 1, write: 'Not Mentioned'."
    ),
    "Low-Pass Filter": (
        "Step 1: Check if a low-pass filter was applied to remove high-frequency noise. Look for phrases like 'low-pass filter', 'LPF', or 'cutoff frequency' related to the attenuation of high-frequency components.",
        "Step 2: If a low-pass filter was identified in Step 1, extract the cutoff frequency and its unit (Hz). Report as: 'Low-pass filter: X Hz'. If no low-pass filter was mentioned or identified in Step 1, write: 'Not Mentioned'."
    ),
    "Downsampling": (
        "Step 1: Identify if the EEG data's sampling rate was reduced. Look for terms like 'downsampled to', 'resampled at a lower frequency', or a change in sampling frequency mentioned after initial acquisition.",
        "Step 2: If downsampling was identified in Step 1, extract the final sampling frequency value and its unit (Hz). Report as: 'Final sampling rate: X Hz'. If not mentioned or identified in Step 1, write: 'Not Mentioned'."
    ),
    "Re-referencing": (
        "Identify the re-referencing scheme applied to the EEG data. Look for phrases such as 're-referenced to', 'referenced to', 'common average reference (CAR)', 'linked mastoids', or specific electrode names used as a reference (e.g., Cz). Report the method used. If not mentioned, write: 'Not Mentioned'."
    ),
    "Visual Inspection (Data)": (
        "Step 1: Determine if the EEG data (segments/trials) underwent visual inspection for artifact rejection. Look for phrases like 'visually inspected for artifacts', 'bad trials were manually removed', or similar descriptions of manual data quality checks.",
        "Step 2: If visual inspection was used (Yes from Step 1), briefly list any reasons mentioned for rejecting data segments/trials (e.g., 'muscle artifacts', 'eye blinks', 'excessive noise', 'drift'). Report as: 'Yes (Reasons: [list of reasons])'. If visual inspection was not mentioned or the answer to Step 1 is No, write: 'Not Mentioned'."
    ),
    "Numerical Criterion (Data)": (
        "Identify if any numerical thresholds or criteria were used to automatically reject bad EEG data segments/trials. Look for statements specifying amplitude limits (e.g., 'trials exceeding ±100 µV were rejected'), variance thresholds, or other quantitative measures for data exclusion. List these criteria. If not mentioned, write: 'Not Mentioned'."
    ),
    "Visual Inspection (Channel)": (
        "Step 1: Determine if individual EEG channels were visually inspected and rejected due to poor quality. Look for phrases like 'bad channels were visually identified', 'noisy channels were manually removed', or similar descriptions of manual channel assessment.",
        "Step 2: If visual inspection was used for channel rejection (Yes from Step 1), specify any criteria mentioned for identifying bad channels (e.g., 'excessive noise', 'flat signal', 'intermittent connectivity'). Report as: 'Yes (Criteria: [list of criteria])'. If visual inspection for channel rejection was not mentioned or the answer to Step 1 is No, write: 'Not Mentioned'."
    ),
    "Numerical Criterion (Channel)": (
        "Identify if any automatic, numerical criteria were used to detect and remove bad EEG channels. Look for specific thresholds or methods mentioned (e.g., 'channels with flat activity for > 5 seconds were removed', 'channels with correlation < 0.8 with neighbors were excluded'). List these criteria. If not mentioned, write: 'Not Mentioned'."
    ),
    "Interpolate Channels": (
        "Determine if any removed EEG channels were subsequently interpolated. If yes, identify the interpolation method used (e.g., 'spherical spline interpolation', 'nearest neighbor interpolation'). Report as: 'Yes (Method: [interpolation method])'. If not mentioned, write: 'Not Mentioned'."
    ),
    "ICA Decomposition": (
        "Identify if Independent Component Analysis (ICA) was performed on the EEG data. If yes, name the specific ICA algorithm used (e.g., 'runica', 'AMICA', 'FastICA', 'infomax ICA'). Report as: 'Yes (Algorithm: [ICA algorithm])'. If not mentioned, write: 'Not Mentioned'."
    ),
    "IC Selection": (
        "Describe the method used to select or reject independent components after ICA decomposition. Was it manual (e.g., based on visual inspection of topographies and time series), automatic (e.g., using algorithms like ICLabel or ADJUST), or semi-automatic (e.g., manual review of components flagged by an algorithm)? List any tools or criteria used for this selection (e.g., 'ICLabel probability', 'correlation with EOG channels'). If not mentioned, write: 'Not Mentioned'."
    ),
    "ASR": (
        "Determine if Artifact Subspace Reconstruction (ASR) was applied to clean the EEG data. If yes, list any specific parameters mentioned for the ASR procedure (e.g., 'burst criterion = 5 standard deviations', 'cutoff frequency'). Report as: 'Yes (Parameters: [list of parameters])'. If not mentioned, write: 'Not Mentioned'."
    ),
    "Epoching": (
        "Identify if the continuous EEG data was segmented into epochs based on specific gait-related events. List the gait events used for epoching (e.g., 'heel-strike', 'toe-off', 'stance phase onset'). If not mentioned, write: 'Not Mentioned'."
    ),
    "Baseline Correction": (
        "Determine if a baseline correction was applied to the epoched EEG data. If yes, specify the time window used as the baseline (e.g., '-200 to 0 ms relative to event onset', 'the 100 ms pre-event interval'). Report as: 'Yes (Window: [baseline window])'. If not mentioned, write: 'Not Mentioned'."
    ),
    "Artifact Rejection/Correction": (
        "Summarize all methods used for artifact rejection or correction mentioned in the text. List all the techniques identified (e.g., 'ICA', 'ASR', 'visual inspection', 'numerical thresholding'). If no specific artifact rejection/correction methods are mentioned, write: 'Not Mentioned'."
    )
}

def query_pubmed(keywords):
    term = '+'.join(keywords.split())
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&retmax=5&term={term}&retmode=json"
    resp = requests.get(url)
    ids = resp.text.split('<Id>')[1:]
    return [i.split('</Id>')[0] for i in ids]

def fetch_fulltext(pmcid):
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmcid}/unicode"
    resp = requests.get(url)
    return resp.text

def extract_methods_section(xml):
    root = ET.fromstring(xml)
    methods = []
    for sec in root.iter('sec'):
        title = sec.find('title')
        if title is not None and 'method' in title.text.lower():
            texts = [p.text for p in sec.findall('p') if p.text]
            methods.append(' '.join(texts))
    return ' '.join(methods)

def call_hf_llm(prompt, hf_token):
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 512}}
    resp = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers, json=payload)
    try:
        return resp.json()[0]["generated_text"]
    except:
        return ""

def extract_parameters(text, hf_token):
    all_prompts = {**study_prompts, **gait_eeg_prompts}
    data = {}
    for key, q in all_prompts.items():
        response = call_hf_llm(f"{q}\n\nText:\n{text}\n\nAnswer:", hf_token)
        data[key] = response.strip().split("Answer:")[-1].strip()
    return data

def visualize_parameters(param_dict):
    G = nx.Graph()
    for key, val in param_dict.items():
        G.add_node(key)
        if val != "Not Mentioned":
            G.add_node(val)
            G.add_edge(key, val)
    fig, ax = plt.subplots()
    nx.draw(G, with_labels=True, node_color='lightblue', node_size=1500, font_size=8, ax=ax)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    st.image(buf)

# Streamlit UI
st.title("Gait EEG Methods Extractor (LLM Agent)")
hf_token = st.text_input("Enter your Hugging Face Token", type="password")
keywords = st.text_input("Enter keywords (e.g., EEG gait analysis)")

if st.button("Run Agent") and hf_token and keywords:
    with st.spinner("Querying PubMed and Processing..."):
        pmc_ids = query_pubmed(keywords)
        st.success(f"Found {len(pmc_ids)} papers.")

        for pmcid in pmc_ids:
            st.subheader(f"Paper ID: {pmcid}")
            xml = fetch_fulltext(pmcid)
            methods = extract_methods_section(xml)
            if not methods:
                st.warning("No methods section found.")
                continue
            param_data = extract_parameters(methods, hf_token)
            st.json(param_data)
            visualize_parameters(param_data)