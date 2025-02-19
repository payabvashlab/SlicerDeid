import logging
import os
import vtk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import csv
from deidLib.dependency_handler import NonSlicerPythonDependencies
dependencies = NonSlicerPythonDependencies()
dependencies.setupPythonRequirements(upgrade=True)
import pandas as pd
from ctk import ctkFileDialog
from datetime import datetime
import time
import shutil
from pathlib import Path
from datetime import datetime
import sys
import cv2
from PIL import Image, ImageDraw, ImageFont
import random
from skimage.measure import label, regionprops
from scipy.ndimage import binary_fill_holes
from skimage.morphology import disk, binary_dilation
        
FACE_MAX_VALUE = 50
FACE_MIN_VALUE = -125

AIR_THRESHOLD = -800
KERNEL_SIZE = 30
ERROR = ""
import pydicom
import numpy as np


class deid(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "deid"  # Human-readable title
        self.parent.categories = ["Utilities"]
        self.parent.dependencies = []
        self.parent.contributors = ["Columbia University"]
        self.parent.helpText = """
This module de-identifies DICOM files by removing patient information based on a given list of patients.
"""
        self.parent.acknowledgementText = """
This file was developed by Sam, Columbia University.
"""

class deidWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        uiWidget = slicer.util.loadUI(self.resourcePath('UI/deid.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)
        uiWidget.setMRMLScene(slicer.mrmlScene)

        self.logic = deidLogic()

        self.ui.inputFolderButton.connect('directoryChanged(QString)', self.updateParameterNodeFromGUI)
        self.ui.outputFolderButton.connect('directoryChanged(QString)', self.updateParameterNodeFromGUI)
        
        self.ui.applyButton.connect('clicked()', self.onApplyButton)
        self.ui.excelFileButton.connect('clicked()', self.onBrowseExcelFile)
        self.ui.deidentifyCheckbox.connect('toggled(bool)', self.updateParameterNodeFromGUI)  # Handle checkbox state
        
        self.initializeParameterNode()

    def initializeParameterNode(self):
        self.setParameterNode(self.logic.getParameterNode())

    def setParameterNode(self, inputParameterNode):
        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)
        if self._parameterNode is not None:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self.updateGUIFromParameterNode()
    
    def updateGUIFromParameterNode(self, caller=None, event=None):
        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return
        self._updatingGUIFromParameterNode = True

        self.ui.inputFolderButton.directory = self._parameterNode.GetParameter("InputFolder")
        excelFile = self._parameterNode.GetParameter("ExcelFile")
        if excelFile:
            self.ui.excelFileButton.text = excelFile
        self.ui.outputFolderButton.directory = self._parameterNode.GetParameter("OutputFolder")
        
        # Check if all required fields have values and enable the "Ally" button
        if len(self._parameterNode.GetParameter("InputFolder"))>1  and len(self._parameterNode.GetParameter("ExcelFile"))>4 and len(self._parameterNode.GetParameter("OutputFolder"))>1 and self._parameterNode.GetParameter("ExcelFile")!="Browse":
            self.ui.applyButton.setEnabled(True)
        else:
            self.ui.applyButton.setEnabled(False)


        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()

        self._parameterNode.SetParameter("InputFolder", self.ui.inputFolderButton.directory)
        self._parameterNode.SetParameter("ExcelFile", self.ui.excelFileButton.text)
        self._parameterNode.SetParameter("OutputFolder", self.ui.outputFolderButton.directory)
        self._parameterNode.SetParameter("Deidentify", str(self.ui.deidentifyCheckbox.isChecked()).lower())  # Set checkbox state

        self._parameterNode.EndModify(wasModified)
        
    def onApplyButton(self):
        try:
            self.ui.progressBar.setValue(0) 
            self.logic.process(
                        self.ui.inputFolderButton.directory,
                        self.ui.excelFileButton.text,
                        self.ui.outputFolderButton.directory,
                        self.ui.deidentifyCheckbox.isChecked(),
                        self.ui.progressBar
            )
        except Exception as e:
            slicer.util.errorDisplay(f"Error: {str(e)}")

    def onBrowseExcelFile(self):
        fileDialog = ctkFileDialog()
        fileDialog.setWindowTitle("Select Excel File")
        fileDialog.setNameFilters(["Excel Files (*.xlsx)", "All Files (*)"])
        fileDialog.setFileMode(ctkFileDialog.ExistingFile)  # Ensure only existing files can be selected
        fileDialog.setOption(ctkFileDialog.DontUseNativeDialog, False)

        # Execute the dialog and get the selected file
        if fileDialog.exec_():  # If the user clicks 'OK'
            selectedFile = fileDialog.selectedFiles()[0]  # Get the first selected file
            self.ui.excelFileButton.text = selectedFile
            # Set full path in parameter node
            self._parameterNode.SetParameter("ExcelFile", selectedFile)

            # Trigger GUI update
            self.updateGUIFromParameterNode()


class deidLogic(ScriptedLoadableModuleLogic):
    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.logger = logging.getLogger("PatientProcessor")

    def setDefaultParameters(self, parameterNode):
        if not parameterNode.GetParameter("InputFolder"):
            parameterNode.SetParameter("InputFolder", "")
        if not parameterNode.GetParameter("ExcelFile"):
            parameterNode.SetParameter("ExcelFile", "")
        if not parameterNode.GetParameter("OutputFolder"):
            parameterNode.SetParameter("OutputFolder", "")
        if not parameterNode.GetParameter("Deidentify"):
            parameterNode.SetParameter("Deidentify", "false")

    def process(self, inputFolder, excelFile, outputFolder, remove_text, progressBar):
        if not os.path.exists(inputFolder):
            raise ValueError(f"Input folder does not exist: {inputFolder}")
        if not os.path.exists(excelFile):
            raise ValueError(f"Excel file does not exist: {excelFile}")
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)
        columns_as_text = ['Accession_number', 'De-identification_ID'] 
        df = pd.read_excel(excelFile, dtype={col: str for col in columns_as_text})
        if ("Accession_number" not in df.columns) or ("De-identification_ID" not in df.columns):
            raise ValueError("Excel file must contain a 'Accession_number' and 'GWTG_ID' column")
            return 0
        else:
            try:
                log_file = os.path.join(outputFolder, "patient_processing.log")
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.INFO)
                file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
                self.logger.info(f"Initialized patient processing module {log_file}")
            except Exception as e:
                self.logger.info(e)
            df['Accession_number'] = df['Accession_number'].astype(str).str.strip()
            df['De-identification_ID'] = df['De-identification_ID'].astype(str).str.strip()
            id_mapping = dict(zip(df['Accession_number'], df['De-identification_ID']))
            dicom_folders = [d for d in os.listdir(inputFolder) if os.path.isdir(os.path.join(inputFolder, d))]
            total_rows = df.shape[0]
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = os.path.join(outputFolder, f'Processed for GWTG_{current_time}')
            os.makedirs(out_path, exist_ok=True)
            for i, foldername in enumerate(dicom_folders):
                if (foldername in id_mapping):
                    dst_folder = ""
                    try:
                        dst_folder = os.path.join(out_path, id_mapping[foldername])
                        processor = DicomProcessor()
                        src_folder = os.path.join(inputFolder, foldername)
                        result = processor.drown_volume(src_folder, dst_folder, 'face', id_mapping[foldername], f"De-identification {id_mapping[foldername]}", remove_text)
                        progressBar.setValue(int((i + 1)* 100/ total_rows)) 
                        slicer.util.showStatusMessage(f"Finished processing foldername {foldername}")
                        self.logger.info(f"Finished processing folder: {foldername}")
                    except Exception as e:
                        self.logger.error(f"Error processing folder {foldername}: {str(e)}")
                        if os.path.exists(dst_folder):
                            shutil.rmtree(dst_folder)
            try:
                folder_list_2 = df['Accession_number'].tolist()  # Convert to string (in case of numbers)
                actual_folders = dicom_folders  # Get folder names in directory
                missing_folders = [folder for folder in folder_list_2 if folder not in actual_folders]
                if len(missing_folders)>0:
                    self.logger.error(f"Missing Folders {missing_folders}")
                    slicer.util.showStatusMessage(f"Missing Folders {missing_folders}")
            except Exception as e:
                self.logger.error(f"Error processing folder {foldername}: {str(e)}")


class deidTest(ScriptedLoadableModuleTest):
    def setUp(self):
        slicer.mrmlScene.Clear()

    def runTest(self):
        self.setUp()
        self.test_deid1()

    def test_deid1(self):
        self.delayDisplay("Starting the test")

        testInputFolder = os.path.join(slicer.app.temporaryPath, "TestInput")
        testOutputFolder = os.path.join(slicer.app.temporaryPath, "TestOutput")
        testExcelFile = os.path.join(slicer.app.temporaryPath, "TestPatients.xlsx")

        os.makedirs(testInputFolder, exist_ok=True)
        os.makedirs(testOutputFolder, exist_ok=True)

        # Create test data
        patientIDs = ["12345", "67890"]
        df = pd.DataFrame({"PatientID": patientIDs})
        df.to_excel(testExcelFile, index=False)

        # Create dummy DICOM files
        import pydicom
        for patientID in patientIDs:
            ds = pydicom.Dataset()
            ds.PatientID = patientID
            ds.PatientName = "Test Patient"
            filePath = os.path.join(testInputFolder, f"{patientID}.dcm")
            ds.save_as(filePath)

        # Run logic
        logic = deidLogic()
        logic.process(testInputFolder, testExcelFile, testOutputFolder)

        # Verify results
        for patientID in patientIDs:
            outputFile = os.path.join(testOutputFolder, f"{patientID}.dcm")
            self.assertTrue(os.path.exists(outputFile))
            ds = pydicom.dcmread(outputFile)
            self.assertEqual(ds.PatientID, "")
            self.assertEqual(ds.PatientName, "")

        self.delayDisplay("Test passed")


class DicomProcessor:
    def __init__(self):
        self.error = ""
        self.net = ""

    def is_dicom(self, file_path):
        try:
            ds = pydicom.dcmread(file_path, force=True)
            try:
                ds.decompress()
                if self.checkCTmeta(ds) == 0:
                    return False
            except Exception:
                if self.checkCTmeta(ds) == 0:
                    return False
            return True
        except Exception:
            return False

    def is_dicom_nometa(self, file_path):
        try:
            ds = pydicom.dcmread(file_path, force=True)
            ds.decompress()
            return True
        except Exception:
            return False

    def list_dicom_directories(self, root_dir):
        dicom_dirs = set()
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if self.is_dicom(file_path):
                    dicom_dirs.add(root)
                else:
                    break
        return list(dicom_dirs)

    def load_scan(self, path):
        p = Path(path)
        if p.is_file():
            slices = pydicom.dcmread(str(p), force=True)
        return slices

    def get_pixels_hu(self, slices):
        image = slices.pixel_array.astype(np.int16)
        image[image == -2000] = 0
        intercept = slices.RescaleIntercept
        slope = slices.RescaleSlope
        if slope != 1:
            image = slope * image.astype(np.float64)
            image = image.astype(np.int16)
        image += np.int16(intercept)
        return np.array(image, dtype=np.int16)

    def binarize_volume(self, volume, air_hu=-800):
        binary_volume = np.zeros_like(volume, dtype=np.uint8)
        binary_volume[volume <= air_hu] = 1
        return binary_volume

    def largest_connected_component(self, binary_image):
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_image, connectivity=8)
        largest_component_index = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
        largest_component_image = np.zeros(labels.shape, dtype=np.uint8)
        largest_component_image[labels == largest_component_index] = 1
        return largest_component_image

    def get_largest_component_volume(self, volume):
        processed_volume = self.largest_connected_component(volume)
        return processed_volume

    def dilate_volume(self, volume, kernel_size=KERNEL_SIZE):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        dilated_volume = cv2.dilate(volume.astype(np.uint8), kernel)
        return dilated_volume

    def apply_mask_and_get_values(self, image_volume, mask_volume):
        masked_volume = image_volume * mask_volume
        unique_values = np.unique(masked_volume)
        unique_values = unique_values[(unique_values > -125) & (unique_values < 50)]
        return unique_values.tolist()

    def apply_random_values_optimized(self, pixels_hu, dilated_volume, unique_values_list):
        new_volume = np.copy(pixels_hu)
        random_indices = np.random.choice(len(unique_values_list), size=np.sum(dilated_volume))
        random_values = np.array(unique_values_list)[random_indices]
        new_volume[dilated_volume == 1] = random_values
        return new_volume

    def person_names_callback(self, ds, elem):
        if elem.VR == "PN":
            elem.value = "anonymous"

    def curves_callback(self, ds, elem):
        if elem.tag.group & 0xFF00 == 0x5000:
            del ds[elem.tag]

    def is_substring_in_list(self, substring, string_list):
        return any(substring in string for string in string_list)
    
    def checkCTmeta(self, ds):
        try:
            modality = ""
            if (0x08, 0x60) in ds:
                modality = ds[0x08, 0x60].value

            modality = [modality] if isinstance(modality, str) else modality
            modality = list(map(lambda x: x.lower().replace(' ', ''), modality))
            check = ["ct", "computedtomography", "ctprotocal"]
            status1 = any(self.is_substring_in_list(c, modality) for c in check)
            imageType = ""
            if (0x08, 0x08) in ds:
                imageType = ds[0x08, 0x08].value
            imageType = [imageType] if isinstance(imageType, str) else imageType
            imageType = list(map(lambda x: x.lower().replace(' ', ''), imageType))
            check = ["original", "primary", "axial"]
            status2 = all(self.is_substring_in_list(c, imageType) for c in check)

            studyDes = ""
            if (0x08, 0x1030) in ds:
                studyDes = ds[0x08, 0x1030].value
            elif (0x08, 0x103e) in ds:
                studyDes = ds[0x08, 0x103e].value
            elif (0x18, 0x15) in ds:
                studyDes = ds[0x18, 0x15].value
            elif (0x18, 0x1160) in ds:
                studyDes = ds[0x18, 0x1160].value
            studyDes = [studyDes] if isinstance(studyDes, str) else studyDes
            studyDes = list(map(lambda x: x.lower().replace(' ', ''), studyDes))
            check = ["head", "brain", "skull"]
            status3 = any(self.is_substring_in_list(c, studyDes) for c in check)

            return int(status1 and status2 and status3)
        except Exception as e:
            self.error = str(e)
        return 0

    # Function to detect text regions using EAST text detector
    def get_data_file_path(self, filename):
        if getattr(sys, 'frozen', False):
            # Running as a bundled executable
            bundle_dir = sys._MEIPASS
        else:
            # Running in development mode
            bundle_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(bundle_dir, filename)

    
    def remove_large_objects(self, mask, max_size):
        labeled_mask = label(mask)  # Label connected components
        if labeled_mask.max() == 0:
            return mask
        new_mask = np.zeros_like(mask, dtype=bool)
        try:
            for region in regionprops(labeled_mask):
                if region.area <= max_size:  # Keep only small objects
                    new_mask[labeled_mask == region.label] = True

            largest_region = max(regionprops(labeled_mask), key=lambda r: r.area)
            largest_mask = (labeled_mask == largest_region.label)
            largest_mask = binary_dilation(largest_mask.astype(np.uint8), disk(4, dtype=bool))
            filled_mask = binary_fill_holes(largest_mask).astype(np.uint8)
            new_mask[filled_mask==1]=0
        except Exception as e:
            return mask
        return new_mask

    def detect_text_regions_east(self, image):
        mask = image.copy()
        mask[image>0]=1
        mask[image < 0] = 0
        mask = self.remove_large_objects(mask, 100)
        mask = binary_dilation(mask.astype(np.uint8), disk(4, dtype=bool))
        return mask

    def save_new_dicom_files(self, original_dir, out_dir, replacer='face', id='GWTG_ID', name='De-identification',
                             remove_text=False):
        dicom_files = [f for f in os.listdir(original_dir) if self.is_dicom(os.path.join(original_dir, f))]
        errors = []
        try:
            dicom_files.sort(
                key=lambda x: int(pydicom.dcmread(os.path.join(original_dir, x), force=True).InstanceNumber))
        except Exception as e:
            print(e)

        for i, dicom_file in enumerate(dicom_files, start=1):
            try:
                ds = self.load_scan(os.path.join(original_dir, dicom_file))

                pixels_hu = self.get_pixels_hu(ds)

                binarized_volume = self.binarize_volume(pixels_hu)
                processed_volume = self.get_largest_component_volume(binarized_volume)
                dilated_volume = self.dilate_volume(processed_volume)

                if replacer == 'face':
                    unique_values_list = self.apply_mask_and_get_values(pixels_hu, dilated_volume - processed_volume)
                elif replacer == 'air':
                    unique_values_list = [0]
                else:
                    try:
                        replacer = int(replacer)
                        unique_values_list = [replacer]
                    except:
                        unique_values_list = self.apply_mask_and_get_values(pixels_hu,
                                                                            dilated_volume - processed_volume)

                if remove_text == True:
                    min_val = np.min(pixels_hu)
                    text_regions = self.detect_text_regions_east(pixels_hu)
                    pixels_hu[text_regions == 1] = min_val
                new_volume = self.apply_random_values_optimized(pixels_hu, dilated_volume, unique_values_list)

                try:
                    ds.decompress()
                except Exception as e:
                    print(e)
                ds.remove_private_tags()

                if "OtherPatientIDs" in ds:
                    delattr(ds, "OtherPatientIDs")
                if "OtherPatientIDsSequence" in ds:
                    del ds.OtherPatientIDsSequence
                ds.walk(self.person_names_callback)
                ds.walk(self.curves_callback)

                ANONYMOUS = "Processed GWTG"
                today = time.strftime("%Y%m%d")
                current_time = datetime.now().strftime("%H%M%S.%f")

                # Iterate over all elements in the dataset
                arr_name=["birthdate", "accessionnumber", "patientname", "patientid", "address", "phone"]
                arr_replace=[today, ANONYMOUS, name, id, "None", 0]
                for tag in ds.dir():
                    # Check if the tag name contains "UID"
                    for k in range(len(arr_name)):
                        condition = arr_name[k]
                        if (condition in tag.lower()):
                            element = ds.data_element(tag)  # Access the DataElement by its name
                            if element:  # Ensure the element exists
                                #print(f"Updating {tag} (Value: {element.value}) to {arr_replace[k]}")
                                element.value = arr_replace[k]
                #requirement tag
                if (0x08, 0x50) not in ds:
                    ds.add_new((0x08, 0x50), 'SH', ANONYMOUS)
                else:
                    ds[0x08, 0x50].value = ANONYMOUS
                if (0x10, 0x10) not in ds:
                    ds.add_new((0x10, 0x10), 'PN', name)
                else:
                    ds[0x10, 0x10].value = name

                if (0x10, 0x20) not in ds:
                    ds.add_new((0x10, 0x20), 'LO', id)
                else:
                    ds[0x10, 0x20].value = id

                if (0x10, 0x30) not in ds:
                    ds.add_new((0x10, 0x30), 'DA', today)
                else:
                    ds[0x10, 0x30].value = today
                #optional type=3, address, phone
                try:
                    ds[0x10, 0x1040].value = ANONYMOUS
                    ds[0x10, 0x2154].value = ANONYMOUS
                except Exception as e:
                    self.error = str(e)
                try:
                    ds[0x08, 0x90].value = ANONYMOUS
                    ds[0x08, 0x1050].value = ANONYMOUS
                    ds[0x08, 0x1060].value = ANONYMOUS
                except Exception as e:
                    self.error = str(e)

                new_slice = (new_volume - ds.RescaleIntercept) / ds.RescaleSlope
                ds.PixelData = new_slice.astype(np.int16).tobytes()
                new_file_name = f"{id}_{i:05d}.dcm"
                final_file_path = os.path.join(out_dir, new_file_name)
                ds.save_as(final_file_path)
            except Exception as e:
                errors.append((dicom_file, str(e)))

        if errors:
            with open(os.path.join(out_dir, 'log.txt'), 'a') as error_file:
                for dicom_file, error in errors:
                    error_file.write(f"File: {dicom_file}, Error: {error}\n")

        return errors

    def drown_volume(self, in_path, out_path, replacer='face', id='GWTG_ID', name='De-identification', remove_text=False):
        try:
            for root, dirs, files in os.walk(in_path):
                relative_path = os.path.relpath(root, in_path)
                out_dir = os.path.join(out_path, relative_path)
                dicom_files = [f for f in files if self.is_dicom(os.path.join(root, f))]
                if dicom_files:
                    os.makedirs(out_dir, exist_ok=True)
                    self.save_new_dicom_files(root, out_dir, replacer, id, name, remove_text)
        except Exception as e:
            with open(os.path.join(out_dir, 'log.txt'), 'a') as error_file:
                error_file.write(f"Error: {e}\n")
            return 0
        return 1