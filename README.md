# Head CT de-identification tool
<h2>This project is under development</h2>

Approximately 15% to 30% of CT scans performed annually in the United States are head CTs [1, 2]. As a rapid and widely accessible modality, head CT is the first line of imaging to evaluate acute brain injury, cerebrovascular accidents, altered mental status, and post-procedural monitoring. Sharing head CT scans across institutions can facilitate the creation of large datasets for training deep learning models to guide treatment decisions in acute clinical settings. 

A critical step for medical image sharing is removal of Protected Health Information (PHI) and Personally Identifiable Information (PII) to safeguard patient privacy and comply with HIPAA regulations. In head CT scans, personal and medical information are included in the DICOM file metadata [3]. Additionally, some scans may contain burned-in text displaying PHI/PII directly on the image. Three-dimensional reconstructions of volumetric brain CTs can also reveal facial features that may compromise patient privacy [4]. 

This 3D Slicer extension is designed to remove PHI from head CT DICOM metadata, detect and eliminate DICOM images with burned-in text, and strip superficial facial tissue at the air–skin interface to prevent facial feature recognition in 3D reconstructed head CTs. This project was in part supported by the American Heart Association (AHA) Stroke Image Sharing Consortium:
https://professional.heart.org/en/research-programs/aha-funding-opportunities/data-grant-stroke-images
https://newsroom.heart.org/news/sharing-brain-images-can-foster-new-neuroscience-discoveries

*Warning: This tool is a work in progress and is currently being validated as part of an AHA-funded research project. For more information, contact at4049@cumc.columbia.edu. Use at your own risk.*

References: 

1.	Cauley, K.A., Y. Hu, and S.W. Fielden, Head CT: Toward Making Full Use of the Information the X-Rays Give. AJNR Am J Neuroradiol, 2021. 42(8): p. 1362-1369.
2.	Sheppard, J.P., et al., Risk of Brain Tumor Induction from Pediatric Head CT Procedures: A Systematic Literature Review. Brain Tumor Res Treat, 2018. 6(1): p. 1-7.
3.	Clunie, D.A., et al., Report of the Medical Image De-Identification (MIDI) Task Group -- Best Practices and Recommendations. ArXiv, 2025.
4.	Collins, S.A., J. Wu, and H.X. Bai, Facial De-identification of Head CT Scans. Radiology, 2020. 296(1): p. 22.



# Axial head CT detection and de-identification algorithm:

In addition to removing PHI and PII, the head CT de-identification tool detects and excludes DICOM images from other imaging modalities or body regions based on the information in file meta-data, restricting the output to axial head CT series only. This reduces the risk of inadvertently transferring unrelated medical images and minimizes the computational resources required for data transfer and storage. 

Using the following steps, the application ensures that only axial head CT DICOM images are processed and saved; and any DICOM files from other modalities (e.g., MRI, PET, X-ray) or body parts (e.g., neck, abdomen) are excluded.

- Step 1: Check the DICOM file header meta-data to ensure that (1) modality is "ct" or "computedtomography" or "ctprotocal" AND (2) the ImageType is "original" and "primary" and "axial"; AND (3) the StudyDescription or SeriesDescription or BodyPartExamined or FilterType is "head" or "brain" or "skull”.

- Step 2: Remove PHI/PII from the DICOM file metadata by identifying the tags listed in the *DICOM header removal* PDF file (<a href="https://github.com/payabvashlab/SlicerDeid/blob/main/documents/dicomTags.pdf"> DICOM header removal.pdf </a>) and replacing them with the string “anonymous.” The patient name is replaced with “Processed for anonymization”.

- Step 3: Blurring of facial features using morphology-based image processing. We will identify the skin–air interface based on air-level (-1000) Hounsfield Unit attenuation in CT scan. Superficial subcutaneous fat tissue is then removed using a kernel size of 20 voxels to prevent facial feature recognition in 3D reconstructions of the scan.

# Installing the Slicer module
1.	Drag and drop a folder "deidXXX" to the Slicer application window.

2.	Select "Add Python scripted modules to the application" in the popup window, and click OK. 

3.	Select which modules to add to load immediately and click Yes. 

4.	The selected modules will be immediately loaded, installed in all libraries, and made available. Run by in Modules/Utilities/Head CT Deidentification
 

# Uninstalling the Slicer module
1.	Select menu Edit/Application Setting

2.	In Modules, Select Module Path and Arrow on the right to remove
 
3.	Select Remove

4.	Click Ok and Restart the Slicer

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
Individuals or organizations wishing to use this software must contact Columbia University at techtransfer@adcu.columbia.edu to obtain a license. Permission to use the software may be granted free of charge on a case-by-case basis. 

