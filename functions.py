#FCUP-LIACD-G6
#File where we define functions that are used in multiple .ipynb files

import os
import pydicom
import numpy as np


## Load dicom images (only CT) in given folder path

def load_dicom_paths(data_dir):
    image_paths = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.dcm'):
                image_paths.append(os.path.join(root, file))
    return image_paths

def load_scan(path):
    paths = load_dicom_paths(path)
    slices = [pydicom.read_file(dcm) for dcm in paths]
    # Sort them by Slice Location
    slices.sort(key=lambda x: float(x.get((0x0020, 0x1041), pydicom.DataElement(0x0020, 0x1041, '0.0')).value))
    # Remove slices that do not have "Slice Location" (if 0.0 then probably means it is a vertical scan)
    filtered_slices = [slice for slice in slices if slice.get((0x0020, 0x1041), pydicom.DataElement(0x0020, 0x1041, '0.0')).value != '0.0']
    # Remove slices that are not CT
    filtered_slices = [slice for slice in slices if slice.get((0x0008,0x0060), pydicom.DataElement(0x0008,0x0060, '0.0')).value == 'CT']
    return filtered_slices

#This is the info that is in the dicom image:
#(0008,0060)	Modality	CT
#(0020,1041)	Slice Location	-125.000000
#(0028,0010)	Rows	512
#(0028,0011)	Columns	512



## Pixels to Hounsfield Unit (HU)

def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    image = image.astype(np.int16)
    image[image == -2000] = 0
    
    for slice_number in range(len(slices)):
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope
        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
        image[slice_number] += np.int16(intercept)
    return np.array(image, dtype=np.int16)
