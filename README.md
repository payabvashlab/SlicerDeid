# De-identification non-contrast head CT
<h2>This project is under development</h2>

Description:

1) Head Computed Tomography (CT) scans contain identifiable data in Digital Imaging and Com-munications in Medicine (DICOM) metadata as well as facial features, raising privacy concerns. This demonstrates the need for effective de-identification tools to protect patient privacy [1]. 
=>This is a Slicer extension removing Personally Identifiable Information (PII) from head CT dicom

2) Link to our project information:

https://professional.heart.org/en/research-programs/aha-funding-opportunities/data-grant-stroke-images <br/>
https://newsroom.heart.org/news/sharing-brain-images-can-foster-new-neuroscience-discoveries

3) One of the contributions of our module is to remove PII from metadata, face [2, 3], and text within images. <br/>
The idea of de-face: eroding the skin and subcutaneous fat of the head and replacing the air around the head with a customizable pixel value. <br/>
The idea of removing text within images: Using morphology and Keeping the largest object, remove small objects < threshold

4) Warning: 
This tools is work in progress being validated in AHA project. Contact at4049@cumc.columbia.edu for more details. Use at your own risk.

5) References:

[1] David A Clunie, Adam Flanders, Adam Taylor, Brad Erickson, Brian Bialecki, David Brundage, et. al., (2023). Report of the Medical Image De-Identification (MIDI) Task Group - Best Practices and Recommendations, arXiv:2303.10473v2 

[2] Scott A. Collins, Jing Wu, Harrison X. Bai. (2020). Facial De-identification of Head CT Scans. Radiology, 296(1), doi:10.1148/radiol.2020192617

[3] https://github.com/kitamura-felipe/face_deid_ct

6) Install as Slicer extension

# Main Algorithm:
- Step 1: Reading the DICOM file

- Step 2: Check DICOM file: modality("ct" or "computedtomography" or "ctprotocal") + ImageType ("original" and "primary" and "axial") + (StudyDescription or SeriesDescription or BodyPartEx-amined or FilterType ("head" or "brain" or "skull”))

- Step 3: Remove Identifiable Metadata Tags
List of all tags we check and remove:
<a href="https://github.com/payabvashlab/SlicerDeid/blob/main/documents/dicomTags.pdf"> DICOM header removal.pdf </a>
Every DICOM tag listed in the Tables need to be replaced by "anonymous" - except patient name use "Processed for anonymization"

- Step 4: Blurring Facial Features with Morphology-Based Image Processing
The kernel size of 20 pixels determines how much fat is removed


# Install Slicer module
1.	Drag and drop a folder "codeXXX" to the Slicer application window.

2.	Select "Add Python scripted modules to the application" in the popup window, and click OK. 

3.	Select which modules to add to load immediately and click Yes. 

4.	The selected modules will be immediately loaded, installed in all libraries, and made available. Run by in Modules/Utilities/Head CT Deidentification
 

# Uninstall Slicer module
1.	Select menu Edit/Application Setting

2.	In Modules, Select Module Path and Arrow on the right to remove
 
3.	Select Remove

4.	Click Ok and Restart Slicer

# Run:
1.	Select Dicom Folder
The structure of a Dicom folder: The Dicom Folder must directly contain patient folders. Each patient folder may contain subdirectory. The application will process each patient file .dcm and the output has the same structure folder inside
2.	Browse to Excel File
The excel sheet input should be adjusted to have 2 columns with following column titles: <b> Accession_number, New_ID </b>
3.	Select Output Folder
4.	Click Apply

## License
Copyright (c) 2025 Columbia University

All rights reserved.

This software and its associated documentation are the intellectual property of Columbia University. Use, reproduction, or distribution of this software is prohibited without express written permission from Columbia University.

Individuals or organizations wishing to use this software must contact Columbia University at techtransfer@adcu.columbia.edu to obtain a license.

Permission to use the software may be granted free of charge on a case-by-case basis. 

Contact: sp4479@columbia.edu
