# De-identification
This project is under development

Head Computed Tomography (CT) scans contain identifiable data in Digital Imaging and Com-munications in Medicine (DICOM) metadata as well as facial features, raising privacy concerns. This demonstrates the need for effective de-identification tools to protect patient privacy [1]. 
=>This is a Slicer extension removing Personally Identifiable Information (PII) from both metadata and image content. The de-tagging procedure has been shown to be effective and accurate on multiple head CT datasets, whereas morphology-based or AI-based methods have effectively reduced the visibility of faces in images [2] without significantly affecting the diagnostic quality of the scans. 

Our method:
The de-identification process in this study consisted of three main steps: reading the DICOM file, re-de-identifying sensitive tags from the metadata, and removing facial features from the image. First, a DICOM reader accessed and loaded the CT data, and specific metadata tags containing identifiable information were removed. For image-based de-identification, a morphology-based and artificial intelligence-based method was applied to detect and blur facial structures, enhancing privacy while preserving relevant diagnostic information. 

More information about DICOM Standards
https://dicom.nema.org/medical/dicom/current/output/html/part15.html#chapter_E

References:

[1] David A Clunie 1, Adam Flanders 2, Adam Taylor 3, Brad Erickson 4, Brian Bialecki 5, David Brundage, et. al., (2023). Report of the Medical Image De-Identification (MIDI) Task Group - Best Practices and Recommendations, arXiv:2303.10473v2 

[2] Scott A. Collins, Jing Wu, Harrison X. Bai. (2020). Facial De-identification of Head CT Scans. Radiology, 296(1), doi:10.1148/radiol.2020192617



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
