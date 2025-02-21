# De-identification
This project is under development

Head Computed Tomography (CT) scans contain identifiable data in Digital Imaging and Com-munications in Medicine (DICOM) metadata as well as facial features, raising privacy concerns. This demonstrates the need for effective de-identification tools to protect patient privacy. 
=>This is a Slicer extension removing Personally Identifiable Information (PII) from both metadata and image content. The de-tagging procedure has been shown to be effective and accurate on multiple head CT datasets, whereas morphology-based or AI-based methods have effectively reduced the visibility of faces in images without significantly affecting the diagnostic quality of the scans. 

Our method:
The de-identification process in this study consisted of three main steps: reading the DICOM file, re-de-identifying sensitive tags from the metadata, and removing facial features from the image. First, a DICOM reader accessed and loaded the CT data, and specific metadata tags containing identifiable information were removed. For image-based de-identification, a morphology-based and artificial intelligence-based method was applied to detect and blur facial structures, enhancing privacy while preserving relevant diagnostic information. 


Install as Slicer extension
Run:
1.	Select Dicom Folder
The structure of a Dicom folder: The Dicom Folder must directly contain patient folders. Each patient folder may contain subdirectory. The application will process each patient file .dcm and the output has the same structure folder inside
2.	Browse to Excel File
The Excel file has two columns: Accession_number, De-identification_ID
3.	Select Output Folder
4.	Click Apply
- Can be set up as a standalone application

## License
This software is licensed under the terms of the Apache Licence Version 2.0
