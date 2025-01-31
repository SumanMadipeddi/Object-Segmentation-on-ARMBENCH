# -*- coding: utf-8 -*-
"""Object_Detection_and_Segmentation_on_ARMBench_100.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1H0GFxluIBkJPsjvlspeuGMJYFlgDgcje

# Perception Of Robotics Project

## Case 1 :  
+ 100 Images for Training
+ 30 images for each of the test
---


### Authors
+ Sooraj
+ Sai
+ Suman
+ Karteek
"""

import os
import random
import matplotlib.pyplot as plt
import cv2
import numpy as np
import torch
import torch.utils.data
import torchvision
from PIL import Image
from pycocotools.coco import COCO

print("The below are the mentioned number of images in each subset")
print("***********************************************************")
print('number of images are' , len(os.listdir('/content/images')))

class ARMBench(torch.utils.data.Dataset):
    def __init__(self, root, annotation, transforms=None):
        self.root = root
        self.transforms = transforms
        self.coco = COCO(annotation)
        self.ids = list(sorted(self.coco.imgs.keys()))
    def __getitem__(self, index):
        coco = self.coco
        img_id = self.ids[index]
        ann_ids = coco.getAnnIds(imgIds=img_id)
        coco_annotation = coco.loadAnns(ann_ids)
        cat_ids = coco.getCatIds()
        path = coco.loadImgs(img_id)[0]['file_name']
        img = Image.open(os.path.join(self.root, path))
        mask = np.stack([np.where(coco.annToMask(ann)>0,1,0) for ann in coco_annotation])
        num_objs = len(coco_annotation)
        boxes = []
        labels = []
        areas = []
        for i in range(num_objs):
            xmin = coco_annotation[i]['bbox'][0]
            ymin = coco_annotation[i]['bbox'][1]
            xmax = xmin + coco_annotation[i]['bbox'][2]
            ymax = ymin + coco_annotation[i]['bbox'][3]
            boxes.append([xmin, ymin, xmax, ymax])
            labels.append(coco_annotation[i]['category_id'])
            areas.append(coco_annotation[i]['area'])
        masks = mask.transpose((1,2,0))
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)
        img_id = torch.tensor([img_id])
        areas = torch.as_tensor(areas, dtype=torch.float32)
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)
        my_annotation = {}
        my_annotation["boxes"] = boxes
        my_annotation["labels"] = labels
        my_annotation["image_id"] = img_id
        my_annotation["area"] = areas
        my_annotation["iscrowd"] = iscrowd
        if self.transforms is not None:
            img = self.transforms(img)
            masks = self.transforms(masks)
        my_annotation["masks"] = masks
        return img, my_annotation
    def __len__(self):
        return len(self.ids)

def get_transform():
    custom_transforms = []
    custom_transforms.append(torchvision.transforms.ToTensor())
    return torchvision.transforms.Compose(custom_transforms)

def random_color_masks(image):
  colors = [[0, 255, 0],[0, 0, 255],[255, 0, 0],[0, 255, 255],[255, 255, 0],[255, 0, 255],[80, 70, 180], [250, 80, 190],[245, 145, 50],[70, 150, 250],[50, 190, 190]]
  r = np.zeros_like(image).astype(np.uint8)
  g = np.zeros_like(image).astype(np.uint8)
  b = np.zeros_like(image).astype(np.uint8)
  r[image==1], g[image==1], b[image==1] = colors[random.randrange(0, 10)]
  colored_mask = np.stack([r,g,b], axis=2)
  return colored_mask

def preprocess(img,pred,threshold=0.5):
  INSTANCE_CATEGORY_NAMES = ["Tote","Object"]
  masks = (pred[0]['masks'] ==True).squeeze().detach().cpu().numpy()
  pred_class = [INSTANCE_CATEGORY_NAMES[i-1] for i in list(pred[0]['labels'].cpu().numpy())]
  pred_boxes = [[(i[0], i[1]), (i[2], i[3])] for i in list(pred[0]['boxes'].detach().cpu().numpy())]
  return masks, pred_boxes, pred_class

def vis_segmentation(images,labels, threshold=0.9, rect_th=3, text_size=3, text_th=3, url=False):
  masks, boxes, pred_cls = preprocess(images,labels,threshold=threshold)
  img = images[0].numpy().transpose(1,2,0)
  img = img*255
  img = img.astype(np.uint8)
  for i in range(len(masks)):
    rgb_mask = random_color_masks(masks[i])
    img = cv2.addWeighted(img, 1, rgb_mask, 0.5, 1)
    pt1 = tuple(int(x) for x in boxes[i][0])
    pt2 = tuple(int(x) for x in boxes[i][1])
    cv2.rectangle(img, pt1, pt2, color=(0, 255, 0), thickness=rect_th)
    cv2.putText(img, pred_cls[i], pt1, cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 255, 0), thickness=text_th)
  return img, pred_cls, masks[1]

images,labels = next(iter(train_dataloader))
plt.imshow(images[0].numpy().transpose(1,2,0))

out,cls,instances = vis_segmentation(images,labels)
plt.imshow(out)

train_data_dir = '/content/images'

train_armbench = '/content/mix_tote_train_100.json'
test_armbench = '/content/mix_tote_test_30.json'
same_obj_test_armbench = '/content/same_obj_test_30.json'
zoomed_out_test_armbench = '/content/zoomed_out_test_30.json'

train_dataset = ARMBench(root=train_data_dir, annotation=train_armbench, transforms=get_transform())
test_dataset = ARMBench(root=train_data_dir, annotation=test_armbench, transforms=get_transform())
same_obj_test_dataset = ARMBench(root=train_data_dir, annotation=same_obj_test_armbench, transforms=get_transform())
zoomed_out_test_dataset = ARMBench(root=train_data_dir, annotation=zoomed_out_test_armbench, transforms=get_transform())


def collate_fn(batch):
    return tuple(zip(*batch))
train_batch_size = 1
test_batch_size = 1
same_obj_test_batch_size = 1
zoomed_out_test_batch_size = 1

train_dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=train_batch_size, shuffle=True, collate_fn=collate_fn)
test_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=test_batch_size, shuffle=False, collate_fn=collate_fn)
same_obj_dataloader = torch.utils.data.DataLoader(same_obj_test_dataset, batch_size=same_obj_test_batch_size, shuffle=True, collate_fn=collate_fn)
zoomed_out_dataloader = torch.utils.data.DataLoader(zoomed_out_test_dataset, batch_size=zoomed_out_test_batch_size, shuffle=False, collate_fn=collate_fn)

len(test_dataset), len(train_dataset), len(same_obj_test_dataset), len(zoomed_out_test_dataset)

print(len(train_dataloader),len(test_dataloader))

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
print(device)

from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
def get_model_instance_segmentation(num_classes):
    model = torchvision.models.detection.maskrcnn_resnet50(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask, hidden_layer, num_classes)
    return model

from tqdm import tqdm
num_classes = 3
num_epochs = 5
model = get_model_instance_segmentation(num_classes)
model.to(device)
params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)
len_dataloader = len(train_dataloader)
print(len_dataloader)
for epoch in tqdm(range(num_epochs)):
  model.train()
  i = 0
  for imgs, annotations in train_dataloader:
    i += 1
    torch.cuda.empty_cache()
    imgs = list(img.to(device) for img in imgs)
    annotations = [{k: v.to(device) for k, v in t.items()} for t in annotations]
    loss_dict = model(imgs, annotations)
    losses = sum(loss for loss in loss_dict.values())
    optimizer.zero_grad()
    losses.backward()
    optimizer.step()
    torch.cuda.empty_cache()
    print(f'Iteration: {i}/{len_dataloader}, Loss: {losses}')

PATH = "model_100.pt"
torch.save(model, PATH)

from tqdm.notebook import tqdm
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
model.eval()
model = model.to(device)
coco_gt = COCO(test_armbench)

coco_results = []

for images, targets in tqdm(test_dataloader):
    torch.cuda.empty_cache()
    images = list(image.to(device) for image in images)
    targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

    outputs = model(images)

    pred_boxes = outputs[0]['boxes'].cpu().detach()
    pred_labels = outputs[0]['labels'].cpu().detach()
    pred_scores = outputs[0]['scores'].cpu().detach()

    image_id = targets[0]['image_id'].item()
    coco_results.extend([
        {'image_id': image_id, 'category_id': pred_labels[i].item(), 'bbox': pred_boxes[i].tolist(), 'score': pred_scores[i].item()}
        for i in range(len(pred_boxes))
    ])

coco_dt = coco_gt.loadRes(coco_results)

coco_eval = COCOeval(coco_gt, coco_dt, iouType='bbox')
coco_eval.evaluate()
coco_eval.accumulate()
coco_eval.summarize()

mAP = coco_eval.stats[0]

print(f"mAP: {mAP}")

from tqdm.notebook import tqdm
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
test_armbench = same_obj_test_armbench
model.eval()
model = model.to(device)
coco_gt = COCO(test_armbench)

coco_results = []

for images, targets in tqdm(same_obj_dataloader):
    torch.cuda.empty_cache()
    images = list(image.to(device) for image in images)
    targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

    outputs = model(images)

    pred_boxes = outputs[0]['boxes'].cpu().detach()
    pred_labels = outputs[0]['labels'].cpu().detach()
    pred_scores = outputs[0]['scores'].cpu().detach()

    image_id = targets[0]['image_id'].item()
    coco_results.extend([
        {'image_id': image_id, 'category_id': pred_labels[i].item(), 'bbox': pred_boxes[i].tolist(), 'score': pred_scores[i].item()}
        for i in range(len(pred_boxes))
    ])

coco_dt = coco_gt.loadRes(coco_results)

coco_eval = COCOeval(coco_gt, coco_dt, iouType='bbox')
coco_eval.evaluate()
coco_eval.accumulate()
coco_eval.summarize()

mAP = coco_eval.stats[0]

print(f"mAP: {mAP}")

from tqdm.notebook import tqdm
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
test_armbench = zoomed_out_test_armbench
model.eval()
model = model.to(device)
coco_gt = COCO(test_armbench)

coco_results = []

for images, targets in tqdm(zoomed_out_dataloader):
    torch.cuda.empty_cache()
    images = list(image.to(device) for image in images)
    targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

    outputs = model(images)

    pred_boxes = outputs[0]['boxes'].cpu().detach()
    pred_labels = outputs[0]['labels'].cpu().detach()
    pred_scores = outputs[0]['scores'].cpu().detach()

    image_id = targets[0]['image_id'].item()
    coco_results.extend([
        {'image_id': image_id, 'category_id': pred_labels[i].item(), 'bbox': pred_boxes[i].tolist(), 'score': pred_scores[i].item()}
        for i in range(len(pred_boxes))
    ])

coco_dt = coco_gt.loadRes(coco_results)

coco_eval = COCOeval(coco_gt, coco_dt, iouType='bbox')
coco_eval.evaluate()
coco_eval.accumulate()
coco_eval.summarize()

mAP = coco_eval.stats[0]

print(f"mAP: {mAP}")

"""# Custom Prediction using the trained model"""

def get_prediction(img_path, model, threshold=0.5, url=False):
  INSTANCE_CATEGORY_NAMES = ["Tote","Object"]
  img = Image.open(img_path)
  transform = get_transform()
  img = transform(img)
  img = img.cuda()
  pred = model([img])
  pred_score = list(pred[0]['scores'].detach().cpu().numpy())
  pred_t = [pred_score.index(x) for x in pred_score if x > threshold][-1]
  masks = (pred[0]['masks'] >0.5).squeeze().detach().cpu().numpy()
  pred_class = [INSTANCE_CATEGORY_NAMES[i-1] for i in list(pred[0]['labels'].cpu().numpy())]
  pred_boxes = [[(i[0], i[1]), (i[2], i[3])] for i in list(pred[0]['boxes'].detach().cpu().numpy())]
  masks = masks[:pred_t+1]
  pred_boxes = pred_boxes[:pred_t+1]
  pred_class = pred_class[:pred_t+1]
  return masks, pred_boxes, pred_class

def instance_segmentation(img_path, model, threshold=0.9, rect_th=3,
                          text_size=3, text_th=3, url=False):
  masks, boxes, pred_cls = get_prediction(img_path, model, threshold=threshold, url=url)
  img = cv2.imread(img_path)
  img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  for i in range(len(masks)):
    rgb_mask = random_color_masks(masks[i])
    img = cv2.addWeighted(img, 1, rgb_mask, 0.8, 0)
    pt1 = tuple(int(x) for x in boxes[i][0])
    pt2 = tuple(int(x) for x in boxes[i][1])
    cv2.rectangle(img, pt1, pt2, color=(0, 255, 0), thickness=rect_th)
    cv2.putText(img, pred_cls[i], pt1, cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 255, 0), thickness=text_th)
  return img, pred_cls, masks[i]

def random_color_masks(image):
  colors = [[0, 255, 0],[0, 0, 255],[255, 0, 0],[0, 255, 255],[255, 255, 0],[255, 0, 255],[80, 70, 180], [250, 80, 190],[245, 145, 50],[70, 150, 250],[50, 190, 190]]
  r = np.zeros_like(image).astype(np.uint8)
  g = np.zeros_like(image).astype(np.uint8)
  b = np.zeros_like(image).astype(np.uint8)
  r[image==1], g[image==1], b[image==1] = colors[random.randrange(0, 10)]
  colored_mask = np.stack([r,g,b], axis=2)
  return colored_mask

input_img = Image.open("/content/train_1.jpg")
plt.imshow(input_img)

model.eval()
img, pred_classes, masks = instance_segmentation('/content/train_1.jpg', model, rect_th=5, text_th=4)
plt.imshow(img)

input_img = Image.open("/content/train_2.jpg")
plt.imshow(input_img)

model.eval()
img, pred_classes, masks = instance_segmentation('/content/train_2.jpg', model, rect_th=5, text_th=4)
plt.imshow(img)

input_img = Image.open("/content/train_3.jpg")
plt.imshow(input_img)

model.eval()
img, pred_classes, masks = instance_segmentation('/content/train_3.jpg', model, rect_th=5, text_th=4)
plt.imshow(img)

input_img = Image.open("/content/test_4.jpg")
plt.imshow(input_img)

model.eval()
img, pred_classes, masks = instance_segmentation('/content/test_4.jpg', model, rect_th=5, text_th=4)
plt.imshow(img)

input_img = Image.open("/content/test_5.jpg")
plt.imshow(input_img)

model.eval()
img, pred_classes, masks = instance_segmentation('/content/test_5.jpg', model, rect_th=5, text_th=4)
plt.imshow(img)