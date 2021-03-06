import numpy as np
import os
import warnings
#import xml.etree.ElementTree as ET

import chainer

from chainercv.datasets.inria import inria_utils
from chainercv.utils import read_image
import re


class INRIABboxDataset(chainer.dataset.DatasetMixin):

    def __init__(self, data_dir='../INRIAPerson', split='Train',
                 use_difficult=False, return_difficult=False):

        id_list_file = os.path.join(
            data_dir, '{0}/pos.lst'.format(split))

        self.ids = list()
        for line in open(id_list_file, 'r', encoding = "ISO-8859-1"):
            line = line.strip()
            line = line.split('/')[2]
            filename = line.split('.')[0]
            self.ids.append(filename)

        self.data_dir = data_dir
        self.split = split
        self.use_difficult = use_difficult
        self.return_difficult = return_difficult

    def __len__(self):
        return len(self.ids)

    def get_example(self, i):
        """Returns the i-th example.

        Returns a color image and bounding boxes. The image is in CHW format.
        The returned image is RGB.

        Args:
            i (int): The index of the example.

        Returns:
            tuple of an image and bounding boxes

        """
        id_ = self.ids[i] # train annotation file
        path = os.path.join(
            self.data_dir, self.split + '/annotations/' + id_ + '.txt')
        
        bbox = list()
        label = list()
        
        for line in open(path, 'r', encoding = "ISO-8859-1"):
            line = line.strip()
            
            if re.search(r'Bounding box for object', line):
                pos = line.find(':') + 1
                axismin, axismax = line[pos:].split('-')
                xmin = int(axismin.split(',')[0].split('(')[1])
                ymin = int(axismin.split(',')[1].split(')')[0])
                xmax = int(axismax.split(',')[0].split('(')[1])
                ymax = int(axismax.split(',')[1].split(')')[0])
                #print('###xmin, ymin, xmax, ymax= ', xmin, ymin, xmax, ymax)
                
                bbox0 = tuple((xmin, ymin, xmax, ymax))
                label0 = 0 if line.split('"')[1] == 'PASperson' else -1
                #print('### box, label=', bbox0, label0)
            
                bbox.append(bbox0)
                label.append(label0)

        bbox = np.stack(bbox).astype(np.float32)
        label = np.stack(label).astype(np.int32)
        
        # Load a image
        img_file = os.path.join(self.data_dir, self.split + '/pos/' + id_ + '.png')
        img = read_image(img_file, color=True)
        
        return img, bbox, label # always not return 'difficult'


