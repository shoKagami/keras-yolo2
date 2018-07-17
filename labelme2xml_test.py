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
    '--image',
    help='path to image folder')

argparser.add_argument(
    '-j',
    '--json',
    help='path to json folder')

argparser.add_argument(
    '-o',
    '--output',
    help='path to xml folder')

def _main_(args):
    dirJson = args.json
    dirImage = args.image
    dirOutput = args.output
    resize = 0.1

    for file in os.listdir(dirJson):
        root = makeDefaultXml(dirImage)
        if(file[-5:] == '.json'):
            inname = os.path.join(dirJson, file)
            with open(inname, 'r') as f_buffer:    
                json_dict = json.load(f_buffer)
            
            fname = SubElement(root, 'filename')
            fname.text = json_dict["imagePath"]
            path = SubElement(root, 'path')
            path.text = os.path.join(dirImage, json_dict["imagePath"])

            im = cv2.imread(path.text)
            h, w = im.shape[:2]
            size = SubElement(root, 'size')
            width = SubElement(size, 'width')
            width.text = str(w)
            height = SubElement(size, 'height')
            height.text = str(h)
            depth = SubElement(size, 'depth')
            depth.text = '3'
            objects = []
            for shape in json_dict["shapes"]:
                xmin = int(resize * shape["points"][0][1])
                ymin = int(resize * shape["points"][0][0])
                xmax = int(resize * shape["points"][2][1])
                ymax = int(resize * shape["points"][2][0])
                bb = {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                objects = SubElement(root, 'object')
                name =  SubElement(objects, 'name')
                name.text = shape["label"]
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

            outname = os.path.join(dirOutput, file[:-5] + ".xml")
            ElementTree(root).write(open(outname, 'wb'))
            ElementTree(root).write(open('hoge.xml', 'wb'))

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