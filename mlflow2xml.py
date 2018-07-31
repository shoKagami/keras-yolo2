import os
import argparse
import json
from xml.etree.ElementTree import Element, ElementTree, SubElement
from xml.dom import minidom
from bs4 import BeautifulSoup

import numpy as np
import cv2

argparser = argparse.ArgumentParser(
    description='convert annotation json data to xml')

argparser.add_argument(
    '-i',
    '--input',
    help='path to annotated data by using mlflow')

argparser.add_argument(
    '-o',
    '--output',
    help='path to xml folder')

def _main_(args):
    dirInput = args.input
    dirOutput = args.output

    for file in os.listdir(dirInput):
        root = makeDefaultXml(dirInput)
        if(file[-5:] == '.json'):
            inname = os.path.join(dirInput, file)
            with open(inname, 'r') as f_buffer:    
                json_dict = json.load(f_buffer)
            
            # '_train.json' -> '.jpg'
            imagename = file[:-11] + '.jpg'
            fname = SubElement(root, 'filename')
            fname.text = imagename
            path = SubElement(root, 'path')
            path.text = os.path.join(dirInput, imagename)

            im = cv2.imread(path.text)
            if im is None:
                continue
            h, w = im.shape[:2]
            size = SubElement(root, 'size')
            width = SubElement(size, 'width')
            width.text = str(w)
            height = SubElement(size, 'height')
            height.text = str(h)
            depth = SubElement(size, 'depth')
            depth.text = '3'
            objects = []
            for shape in json_dict["detectionAnnotations"]:
                points = np.array(shape["boundingRect"])
                points_min = np.min(points, axis=0)
                points_max = np.max(points, axis=0)
                
                xmin = points_min[0]
                ymin = points_min[1]
                xmax = points_max[0]
                ymax = points_max[1]
                bb = {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                objects = SubElement(root, 'object')
                if "object_type" in shape:
                    name =  SubElement(objects, 'name')
                    name.text = shape["object_type"]
                pose =  SubElement(objects, 'pose')
                pose.text = 'Unspecified'
                truncated =  SubElement(objects, 'truncated')
                truncated.text = '0'
                difficult =  SubElement(objects, 'difficult')
                difficult.text = '0'
                bnbbox =  SubElement(objects, 'bndbox')
                xmin_ =  SubElement(bnbbox, 'xmin')
                xmin_.text = str(xmin)
                ymin_ =  SubElement(bnbbox, 'ymin')
                ymin_.text = str(ymin)
                xmax_ =  SubElement(bnbbox, 'xmax')
                xmax_.text = str(xmax)
                ymax_ =  SubElement(bnbbox, 'ymax')
                ymax_.text = str(ymax)

            outname = os.path.join(dirOutput, file[:-11] + ".xml")
            ElementTree(root).write(open(outname, 'wb'))

def makeDefaultXml(folderName):
    root = Element('annotation')
    source = SubElement(root, 'source')
    database = SubElement(source, 'database')
    database.text = 'Unknown'
    folder = SubElement(root, 'folder')
    folder.text = folderName
    segmented = SubElement(root, 'segmented')
    segmented.text = '0'

    return root

if __name__ == '__main__':
    args = argparser.parse_args()
    _main_(args)