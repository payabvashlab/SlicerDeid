# De-identification
This project is under development

Head Computed Tomography (CT) scans contain identifiable data in Digital Imaging and Com-munications in Medicine (DICOM) metadata as well as facial features, raising privacy concerns. This demonstrates the need for effective de-identification tools to protect patient privacy [1]. 
=>This is a Slicer extension removing Personally Identifiable Information (PII) from head CT dicom

One of the contributions of our module is to remove PII from metadata, face [2, 3], and text within images.

List of all tags we check and remove:
 <img src="https://github.com/payabvashlab/SlicerDeid/blob/main/images/metaTag.png" />

The idea of de-face:
- eroding the skin and subcutaneous fat of the head
- replacing the air around the head with a customizable pixel value. 

References:

[1] David A Clunie 1, Adam Flanders 2, Adam Taylor 3, Brad Erickson 4, Brian Bialecki 5, David Brundage, et. al., (2023). Report of the Medical Image De-Identification (MIDI) Task Group - Best Practices and Recommendations, arXiv:2303.10473v2 

[2] Scott A. Collins, Jing Wu, Harrison X. Bai. (2020). Facial De-identification of Head CT Scans. Radiology, 296(1), doi:10.1148/radiol.2020192617

[3] https://github.com/kitamura-felipe/face_deid_ct



Install as Slicer extension
<br/>
# Run:
1.	Select Dicom Folder
The structure of a Dicom folder: The Dicom Folder must directly contain patient folders. Each patient folder may contain subdirectory. The application will process each patient file .dcm and the output has the same structure folder inside
2.	Browse to Excel File
The Excel file has two columns: Accession_number, De-identification_ID
3.	Select Output Folder
4.	Click Apply
- Can be set up as a standalone application

## License
This software is licensed under the terms of the Apache Licence Version 2.0
