# De-identification non-contrast head CT
<h2>This project is under development</h2>

1) Head Computed Tomography (CT) scans contain identifiable data in Digital Imaging and Com-munications in Medicine (DICOM) metadata as well as facial features, raising privacy concerns. This demonstrates the need for effective de-identification tools to protect patient privacy [1]. 
=>This is a Slicer extension removing Personally Identifiable Information (PII) from head CT dicom

2) Link to our project information:
https://professional.heart.org/en/research-programs/aha-funding-opportunities/data-grant-stroke-images <br/>
https://newsroom.heart.org/news/sharing-brain-images-can-foster-new-neuroscience-discoveries

3) List of all tags we check and remove:
<a href="https://github.com/payabvashlab/SlicerDeid/documents/DICOM header removal.pdf"> DICOM header removal.pdf </a>

4) One of the contributions of our module is to remove PII from metadata, face [2, 3], and text within images. <br/>
The idea of de-face: eroding the skin and subcutaneous fat of the head and replacing the air around the head with a customizable pixel value. <br/>
The idea of removing text within images: Using morphology and Keeping the largest object, remove small objects < threshold

5) Warning: 
This tools is work in progress being validated in AHA project. Contact at4049@cumc.columbia.edu for more details. Use at your own risk.

6) References:

[1] David A Clunie, Adam Flanders, Adam Taylor, Brad Erickson, Brian Bialecki, David Brundage, et. al., (2023). Report of the Medical Image De-Identification (MIDI) Task Group - Best Practices and Recommendations, arXiv:2303.10473v2 

[2] Scott A. Collins, Jing Wu, Harrison X. Bai. (2020). Facial De-identification of Head CT Scans. Radiology, 296(1), doi:10.1148/radiol.2020192617

[3] https://github.com/kitamura-felipe/face_deid_ct

7) Install as Slicer extension


# Run:
1.	Select Dicom Folder
The structure of a Dicom folder: The Dicom Folder must directly contain patient folders. Each patient folder may contain subdirectory. The application will process each patient file .dcm and the output has the same structure folder inside
2.	Browse to Excel File
The Excel file has two columns: Accession_number, De-identification_ID
3.	Select Output Folder
4.	Click Apply

## License
This software is licensed under the terms of the Apache Licence Version 2.0
