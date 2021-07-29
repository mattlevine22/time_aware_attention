# run pre-processing (unsure if order matters...some are clearly dependent on previous)
python3 preprocessing_ICU_PAT_ADMIT.py
python3 preprocessing_DIAGNOSES_PROCEDURES.py
python3 preprocessing_reduce_outputs.py
python3 preprocessing_reduce_charts.py # took 6 minutes... 331it [06:22,  1.16s/it]
python3 preprocessing_merge_charts_outputs.py
python3 preprocessing_CHARTS_PRESCRIPTIONS.py
python3 preprocessing_create_arrays.py
