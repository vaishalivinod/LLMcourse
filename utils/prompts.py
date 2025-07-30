# EEG prompts
eeg_prompts = {
    "Experimental task": "What experimental task or cognitive paradigm was used in this study (e.g., auditory oddball, visual oddball, Go/No-Go, resting state)? Report the specific task if mentioned. If not mentioned, write: 'Not Mentioned'.",
    "EEG system": "Which EEG recording system or amplifier was used in this study (e.g., Biosemi, Brain Products, Neuroscan)? Report the name. If not mentioned, write: 'Not Mentioned'.",
    "Number of EEG channels": "How many EEG channels were recorded? Extract the number (e.g., 32, 64, 128). If not mentioned, write: 'Not Mentioned'.",
    "Analysis software": "What software/toolbox was used for EEG data analysis (e.g., EEGLAB, FieldTrip, MNE)? Report the name(s). If not mentioned, write: 'Not Mentioned'.",
    "Bandpass filter": "EEG data are often filtered using a bandpass filter to retain frequencies in a specific range (e.g., 0.1–30 Hz). Search the text and extract any such filtering range. Report as: 'Bandpass filter: X Hz - Y Hz'. If only a high-pass or low-pass is mentioned, say so. If no filter is mentioned, write: 'Not Mentioned'.",
    "High-pass filter": "A high-pass filter removes slow signal drifts. Extract the high-pass cutoff frequency in Hz. If only bandpass is mentioned, extract lower bound. If not mentioned, write: 'Not Mentioned'.",
    "Low-pass filter": "A low-pass filter removes fast noise. Extract the low-pass cutoff frequency in Hz. If only bandpass is mentioned, extract upper bound. If not mentioned, write: 'Not Mentioned'.",
    "Downsampling": "Downsampling reduces sampling rate (e.g., from 1000 Hz to 250 Hz). Extract the final sampling frequency. Report as: 'Final sampling rate: X Hz'. If not mentioned, write: 'Not Mentioned'.",
    "Re-referencing": "EEG data may be re-referenced (e.g., to Cz, average, mastoids). Identify the re-referencing method. If not mentioned, write: 'Not Mentioned'.",
    "Visual inspection data": "Was visual inspection used to reject bad EEG segments/trials? Answer 'Yes' or 'No'. If yes, briefly list reasons (e.g., muscle artifacts, drift). If not mentioned, write: 'Not Mentioned'.",
    "Numerical criterion/function data": "Were numerical criteria used to reject bad EEG data (e.g., amplitude > ±100 µV)? List them. If not mentioned, write: 'Not Mentioned'.",
    "Visual inspection channel": "Was visual inspection used to reject bad EEG channels (e.g., noisy, flat)? Answer 'Yes' or 'No', and list criteria if any. If not mentioned, write: 'Not Mentioned'.",
    "Numerical criterion/function channel": "Were bad channels removed using automatic criteria (e.g., flat > 5s, correlation < 0.8)? List criteria. If not mentioned, write: 'Not Mentioned'.",
    "Interpolate channels": "Were removed EEG channels interpolated? If yes, name method (e.g., spherical spline). If method not mentioned, write: 'Interpolation performed, method not specified'. If not mentioned, write: 'Not Mentioned'.",
    "ICA decomposition": "Was ICA used (e.g., runica, AMICA, FastICA)? If yes, name the algorithm. If algorithm not mentioned, write: 'ICA performed, algorithm not specified'. If not mentioned, write: 'Not Mentioned'.",
    "IC selection": "After ICA, how were components selected or rejected? Was it manual, automatic, or semi-automatic? List tools or criteria (e.g., ICLabel, EOG correlation). If not mentioned, write: 'Not Mentioned'.",
    "ASR": "Artifact Subspace Reconstruction (ASR) is used to clean EEG data by identifying artifact-contaminated segments using a clean subspace (e.g., clean_rawdata in EEGLAB). Was ASR used? If yes, report 'ASR performed' and list any parameters (e.g., burst criterion = 5). If method not stated, say 'ASR performed, parameters not specified'. If not mentioned, write: 'Not Mentioned'."
    }

# Study Description Prompts
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

# Revised prompt definitions for Elicit

study_des = {
"What is the cohort studied in the paper? (e.g., healthy young adults, Parkinson's patients)"
"How many subjects were included in the study?"
"What gait task was performed during EEG recording? (e.g., overground walking, treadmill, obstacle navigation)"
"Was there a secondary task involved during the gait? If yes, describe it."
"What EEG system/manufacturer was used? (e.g., BioSemi, Brain Products)"
"How many EEG channels were recorded?"
"What type of EEG electrodes/channels were used? (e.g., active/passive, wet/dry)"
"Was a dual-layer EEG cap used in the study?"
"What was the EEG sampling frequency in Hz?"
"What software was used for EEG analysis? (e.g., EEGLAB, BrainVision Analyzer)"
}
pre_ICA = {
    "What preprocessing steps were applied before ICA? Please extract steps such as,"
    "Channel rejection method or criteria"
    "Segment/artifact correction methods"
    "Downsampling frequency"
    "Band-pass, high-pass, low-pass, or band-stop filter settings"
    "Line noise removal method (e.g., CleanLine, notch filter)"
    "Re-referencing strategy"
    "Artifact Subspace Reconstruction (ASR) usage"
    "iCanClean usage"
    "Epoching method (if any)"
}

ICA = {
    "What ICA algorithm was used (e.g., Infomax, FastICA)?"
    "How many ICA components were computed?"
    "How were components selected for rejection? (e.g., ICLabel, manual, MARA)"
    "What criteria were used for rejecting components?"
    "Was IC clustering performed? If so, what method?"
}

post_ICA = {
    "What preprocessing steps were applied after ICA? Include if any:"
    "Channel/segment rejection"
    "Filter settings (high-pass, low-pass, band-pass)"
    "Re-referencing"
    "Channel interpolation"
    "Downsampling"
    "Epoching strategy"
    "Source localization techniques"
    "Any analysis of 1/f component or baseline correction"
}

flow_preprocessing_steps = {"List the full sequence of EEG preprocessing steps described in the paper in the order they were applied. Include all relevant filters, re-referencing, artifact rejection, ICA, and post-ICA processing. List them as a step-by-step procedure. If not reported or unclear, write 'Not reported'"}