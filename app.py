import re
import streamlit as st
import pandas as pd

def extract_patient_id(text):
    match = re.search(r"Patient ID:\s*(\d+)", text)
    return match.group(1) if match else ""

def extract_age(text):
    match = re.search(r"Age:\s*(\d+)", text)
    return match.group(1) if match else ""

def extract_gender(text):
    match = re.search(r"Gender:\s*(\w+)", text)
    return match.group(1) if match else ""

def extract_diagnosis(text):
    diagnosis = {}
    cancer_type_match = re.search(r"prostate cancer", text, re.IGNORECASE)
    if cancer_type_match:
        diagnosis["Cancer Type"] = "prostate cancer"
    diagnosis_date_match = re.search(r"diagnosed with prostate cancer in ([\w\s]+ \d{4})", text)
    if diagnosis_date_match:
        diagnosis["Diagnosis Date"] = diagnosis_date_match.group(1)
    gleason_score_match = re.search(r"Gleason score was (\d+)", text)
    if gleason_score_match:
        diagnosis["Gleason Score"] = gleason_score_match.group(1)
    pathologic_stage_match = re.search(r"pathologic stage at diagnosis was (pT\w+)", text, re.IGNORECASE)
    if pathologic_stage_match:
        diagnosis["Pathologic Stage"] = pathologic_stage_match.group(1)
    return diagnosis

def extract_medical_history(text):
    history = []
    comorbidities = re.findall(r"history of ([\w\s]+)", text, re.IGNORECASE)
    for comorbidity in comorbidities:
        history.append({"Comorbidity": comorbidity})
    prior_cancer_history_match = re.search(r"No prior history of cancer", text, re.IGNORECASE)
    if prior_cancer_history_match:
        history.append({"Prior Cancer History": "No prior history of cancer"})
    return history

def extract_disease_states(text):
    states = []
    disease_state_matches = re.findall(r"The disease progressed to ([\w\s]+) until ([\w\s]+ \d{4})", text)
    for match in disease_state_matches:
        states.append({"Disease State": match[0], "Start Date": "", "End Date": match[1]})
    post_prostatectomy_match = re.search(r"post-prostatectomy state until ([\w\s]+ \d{4})", text)
    if post_prostatectomy_match:
        states.append({"Disease State": "post-prostatectomy state", "Start Date": "", "End Date": post_prostatectomy_match.group(1)})
    adjuvant_treatment_match = re.search(r"Adjuvant treatment with ([\w\s]+) commenced in ([\w\s]+ \d{4}) and concluded in ([\w\s]+ \d{4})", text)
    if adjuvant_treatment_match:
        states.append({"Disease State": "adjuvant treatment", "Start Date": adjuvant_treatment_match.group(2), "End Date": adjuvant_treatment_match.group(3)})
    biochemical_recurrence_match = re.search(r"biochemical recurrence detected in ([\w\s]+ \d{4})", text)
    if biochemical_recurrence_match:
        states.append({"Disease State": "biochemical recurrence", "Start Date": biochemical_recurrence_match.group(1), "End Date": ""})
    return states

def extract_procedures(text):
    procedures = []
    procedure_matches = re.findall(r"Following ([\w\s]+) in ([\w\s]+ \d{4})", text)
    for match in procedure_matches:
        procedures.append({"Procedure": match[0], "Date": match[1], "Description": ""})
    return procedures

def extract_treatments(text):
    treatments = []
    treatment_matches = re.findall(r"([A-Za-z\s]+) therapy commenced in ([\w\s]+ \d{4}) and concluded in ([\w\s]+ \d{4})", text)
    for match in treatment_matches:
        treatments.append({"Treatment": match[0] + " therapy", "Start Date": match[1], "End Date": match[2], "Description": ""})
    hormonal_therapy_matches = re.findall(r"hormonal therapy with ([\w\s]+) injections every 3 months until ([\w\s]+ \d{4})", text)
    for match in hormonal_therapy_matches:
        treatments.append({"Treatment": "hormonal therapy", "Start Date": "", "End Date": match[1], "Description": match[0] + " injections every 3 months"})
    current_treatment_match = re.search(r"Current treatment includes second-line hormonal therapy with ([\w\s]+)", text)
    if current_treatment_match:
        treatments.append({"Treatment": "second-line hormonal therapy", "Start Date": "", "End Date": "", "Description": current_treatment_match.group(1)})
    return treatments

def extract_lab_results(text):
    results = []
    lab_result_matches = re.findall(r"PSA levels of ([\d\.]+) ng/mL as of ([\w\s]+ \d{4})", text)
    for match in lab_result_matches:
        results.append({"Lab Result": "PSA levels", "Date": match[1], "Value": match[0] + " ng/mL"})
    cbc_match = re.search(r"Complete blood count from ([\w\s]+ \d{4}) showed WBC: ([\d\.]+), RBC: ([\d\.]+), Platelets: (\d+)", text)
    if cbc_match:
        results.append({"Lab Result": "Complete blood count", "Date": cbc_match.group(1), "Value": "WBC: " + cbc_match.group(2) + ", RBC: " + cbc_match.group(3) + ", Platelets: " + cbc_match.group(4)})
    return results

def extract_imaging_studies(text):
    studies = []
    imaging_study_matches = re.findall(r"Imaging studies reveal ([\w\s]+) as of the latest ([\w\s]+) in ([\w\s]+ \d{4})", text)
    for match in imaging_study_matches:
        studies.append({"Imaging Study": match[1], "Date": match[2], "Findings": match[0]})
    return studies

def extract_medications(text):
    medications = []
    medication_matches = re.findall(r"Current medications include ([\w\s]+) starting ([\w\s]+ \d{4}), with a daily dosage of (\d+ mg)", text)
    for match in medication_matches:
        medications.append({"Medication": match[0], "Start Date": match[1], "End Date": "", "Dosage": match[2]})
    return medications

def process_input(text):
    structured_data = {
        "Patient ID": extract_patient_id(text),
        "Age": extract_age(text),
        "Gender": extract_gender(text),
        "Diagnosis": extract_diagnosis(text),
        "Medical History": extract_medical_history(text),
        "Disease States": extract_disease_states(text),
        "Procedures": extract_procedures(text),
        "Treatments": extract_treatments(text),
        "Lab Results": extract_lab_results(text),
        "Imaging Studies": extract_imaging_studies(text),
        "Medications": extract_medications(text)
    }
    return structured_data

def convert_to_csv(structured_data):
    data = []
    for section, entries in structured_data.items():
        if isinstance(entries, list):
            for entry in entries:
                row = {"Section": section}
                row.update(entry)
                data.append(row)
        else:
            row = {"Section": section}
            row.update({section: entries})  # Update with a dictionary
            data.append(row)
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def convert_to_text(structured_data):
    text_data = ""
    if "Patient ID" in structured_data:
        text_data += f"Patient ID: {structured_data['Patient ID']}\n"
    if "Age" in structured_data:
        text_data += f"Age: {structured_data['Age']}\n"
    if "Gender" in structured_data:
        text_data += f"Gender: {structured_data['Gender']}\n"

    if "Diagnosis" in structured_data:
        text_data += "Diagnosis:\n"
        diagnosis = structured_data['Diagnosis']
        for key, value in diagnosis.items():
            text_data += f"  - {key}: {value}\n"

    if "Medical History" in structured_data:
        text_data += "Medical History:\n"
        medical_history = structured_data['Medical History']
        for entry in medical_history:
            for key, value in entry.items():
                text_data += f"  - {key}: {value}\n"

    if "Disease States" in structured_data:
        text_data += "Disease States:\n"
        disease_states = structured_data['Disease States']
        for state in disease_states:
            for key, value in state.items():
                text_data += f"  - {key}: {value}\n"

    if "Procedures" in structured_data:
        text_data += "Procedures:\n"
        procedures = structured_data['Procedures']
        for procedure in procedures:
            for key, value in procedure.items():
                                text_data += f"  - {key}: {value}\n"

    if "Treatments" in structured_data:
        text_data += "Treatments:\n"
        treatments = structured_data['Treatments']
        for treatment in treatments:
            for key, value in treatment.items():
                text_data += f"  - {key}: {value}\n"

    if "Lab Results" in structured_data:
        text_data += "Lab Results:\n"
        lab_results = structured_data['Lab Results']
        for result in lab_results:
            for key, value in result.items():
                text_data += f"  - {key}: {value}\n"

    if "Imaging Studies" in structured_data:
        text_data += "Imaging Studies:\n"
        imaging_studies = structured_data['Imaging Studies']
        for study in imaging_studies:
            for key, value in study.items():
                text_data += f"  - {key}: {value}\n"

    if "Medications" in structured_data:
        text_data += "Medications:\n"
        medications = structured_data['Medications']
        for medication in medications:
            for key, value in medication.items():
                text_data += f"  - {key}: {value}\n"

    return text_data

def main():
    st.title("Structured Patient Data Converter")
    
    input_data = st.text_area("Input Data", height=300)
    uploaded_file = st.file_uploader("Or upload a text file", type=["txt"])

    if st.button("Generate CSV"):
        if uploaded_file is not None:
            input_data = uploaded_file.read().decode("utf-8")
        
        if input_data:
            structured_data = process_input(input_data)
            st.json(structured_data)
            
            csv_data = convert_to_csv(structured_data)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="structured_data.csv",
                mime="text/csv"
            )
        else:
            st.warning("Please provide input data.")

    if st.button("Generate Text"):
        if uploaded_file is not None:
            input_data = uploaded_file.read().decode("utf-8")
        
        if input_data:
            structured_data = process_input(input_data)
            text_data = convert_to_text(structured_data)
            st.text_area("Structured Data in Text Format", value=text_data, height=300)
            
            st.download_button(
                label="Download Text",
                data=text_data,
                file_name="structured_data.txt",
                mime="text/plain"
            )
        else:
            st.warning("Please provide input data.")

if __name__ == "__main__":
    main()

