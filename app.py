import re
import streamlit as st
import json

# Precompile regex patterns
age_pattern = re.compile(r"Age:\s*(\d+)")
gender_pattern = re.compile(r"Gender:\s*(\w+)")
name_pattern = re.compile(r"Patient Name:\s*([\w]+)")


def extract_name(text):
    match = name_pattern.search(text)
    return match.group(1).strip() if match else ""

def extract_age(text):
    match = age_pattern.search(text)
    return int(match.group(1)) if match else None

def extract_gender(text):
    match = gender_pattern.search(text)
    return match.group(1) if match else ""

def extract_diagnosis(text):
    diagnosis = {}
    cancer_type_match = re.search(r"prostate cancer", text, re.IGNORECASE)
    if cancer_type_match:
        diagnosis["cancerType"] = "Prostate Cancer"
    diagnosis_date_match = re.search(r"diagnosed with prostate cancer in ([\w\s]+ \d{4})", text)
    if diagnosis_date_match:
        diagnosis["diagnosisDate"] = diagnosis_date_match.group(1)
    gleason_score_match = re.search(r"Gleason score was (\d+)", text)
    if gleason_score_match:
        diagnosis["gleason_score"] = int(gleason_score_match.group(1))  # Convert to int for JSON
    pathologic_stage_match = re.search(r"pathologic stage at diagnosis was (pT\w+)", text, re.IGNORECASE)
    if pathologic_stage_match:
        diagnosis["pathologicStage"] = pathologic_stage_match.group(1)
    return diagnosis

def extract_medical_history(text):
    history = []
    comorbidities = re.findall(r"history of ([\w\s]+)", text, re.IGNORECASE)
    for comorbidity in comorbidities:
        history.append(comorbidity)
    prior_cancer_history_match = re.search(r"No prior history of cancer", text, re.IGNORECASE)
    if prior_cancer_history_match:
        history.append("No prior history of cancer")
    return history

def extract_disease_states(text):
    states = []
    disease_state_matches = re.findall(r"The disease progressed to ([\w\s]+) until ([\w\s]+ \d{4})", text)
    for match in disease_state_matches:
        states.append({"state": match[0], "endDate": match[1]})
    post_prostatectomy_match = re.search(r"post-prostatectomy state until ([\w\s]+ \d{4})", text)
    if post_prostatectomy_match:
        states.append({"state": "post-prostatectomy state", "endDate": post_prostatectomy_match.group(1)})
    adjuvant_treatment_match = re.search(r"Adjuvant treatment with ([\w\s]+) commenced in ([\w\s]+ \d{4}) and concluded in ([\w\s]+ \d{4})", text)
    if adjuvant_treatment_match:
        states.append({"state": "adjuvant treatment", "startDate": adjuvant_treatment_match.group(2), "endDate": adjuvant_treatment_match.group(3)})
    biochemical_recurrence_match = re.search(r"biochemical recurrence detected in ([\w\s]+ \d{4})", text)
    if biochemical_recurrence_match:
        states.append({"state": "biochemical recurrence", "startDate": biochemical_recurrence_match.group(1)})
    return states

def extract_procedures(text):
    procedures = []
    procedure_matches = re.findall(r"Following ([\w\s]+) in ([\w\s]+ \d{4})", text)
    for match in procedure_matches:
        procedures.append({"type": match[0], "date": match[1], "description": match[0]})
    return procedures

def extract_treatments(text):
    treatments = []
    treatment_matches = re.findall(r"([A-Za-z\s]+) therapy commenced in ([\w\s]+ \d{4}) and concluded in ([\w\s]+ \d{4})", text)
    for match in treatment_matches:
        treatments.append({"type": match[0] + " therapy", "start_date": match[1], "end_date": match[2]})
    hormonal_therapy_matches = re.findall(r"hormonal therapy with ([\w\s]+) injections every 3 months until ([\w\s]+ \d{4})", text)
    for match in hormonal_therapy_matches:
        treatments.append({"type": "hormonal therapy", "end_date": match[1], "description": match[0] + " injections every 3 months"})
    current_treatment_match = re.search(r"Current treatment includes second-line hormonal therapy with ([\w\s]+)", text)
    if current_treatment_match:
        treatments.append({"type": "second-line hormonal therapy", "description": current_treatment_match.group(1)})
    return treatments

def extract_lab_results(text):
    results = []
    lab_result_matches = re.findall(r"PSA levels of ([\d\.]+) ng/mL as of ([\w\s]+ \d{4})", text)
    for match in lab_result_matches:
        results.append({"test": "PSA levels", "date": match[1], "value": float(match[0]), "unit": "ng/mL"})  # Convert value to float for JSON
    cbc_match = re.search(r"Complete blood count from ([\w\s]+ \d{4}) showed WBC: ([\d\.]+), RBC: ([\d\.]+), Platelets: (\d+)", text)
    if cbc_match:
        results.append({"test": "Complete blood count", "date": cbc_match.group(1), "value": {"wbc": float(cbc_match.group(2)), "rbc": float(cbc_match.group(3)), "platelets": int(cbc_match.group(4))}})
    return results

def extract_imaging_studies(text):
    studies = []
    imaging_study_matches = re.findall(r"Imaging studies reveal ([\w\s]+) as of the latest ([\w\s]+) in ([\w\s]+ \d{4})", text)
    for match in imaging_study_matches:
        studies.append({"type": match[1], "date": match[2], "findings": match[0]})
    return studies

def extract_medications(text):
    medications = []
    medication_matches = re.findall(r"Current medications include ([\w\s]+) starting ([\w\s]+ \d{4}), with a daily dosage of (\d+ mg)", text)
    for match in medication_matches:
        medications.append({"name": match[0], "start_date": match[1], "dosage": match[2]})
    return medications

def process_input(text):
    name = extract_name(text)
    age = extract_age(text)
    gender = extract_gender(text)
    diagnosis = extract_diagnosis(text)
    structured_data = {
        "name": name,
        "age": age,
        "gender": gender,
        "cancerType": diagnosis.get("cancerType", ""),
        "diagnosisDate": diagnosis.get("diagnosisDate", ""),
        "gleason_score": int(diagnosis.get("gleason_score", "")),  # Convert to int for JSON
        "pathologicStage": diagnosis.get("pathologicStage", ""),
        "comorbidities": extract_medical_history(text),
        "diseaseStates": extract_disease_states(text),
        "procedures": extract_procedures(text),
        "treatment": extract_treatments(text),
        "labResults": extract_lab_results(text),
        "imagingStudies": extract_imaging_studies(text),
        "medications": extract_medications(text)
    }
    return structured_data

def main():
    st.title("Structured Patient Data Converter")
    
    input_data = st.text_area("Input Data", height=300)
    uploaded_file = st.file_uploader("Or upload a text file", type=["txt"])

    if st.button("Generate JSON"):
        if uploaded_file is not None:
            input_data = uploaded_file.read().decode("utf-8")
        
        if input_data:
            structured_data = process_input(input_data)
            st.json(structured_data)
            
            json_data = json.dumps(structured_data, indent=4)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="structured_data.json",
                mime="application/json"
            )
        else:
            st.warning("Please provide input data.")

if __name__ == "__main__":
    main()
