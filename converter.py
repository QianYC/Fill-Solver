import cv2
import numpy as np
from sklearn.cluster import DBSCAN
import functools
import sys
import config

class Converter():
	def __init__(self):
		self.positions=[]

	def to_matrix(self,path):
		img = cv2.imread(path)
		grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		grey = cv2.resize(grey, (400, 600))
		# 去掉menu bar
		grey = grey[45:600, 0:400]
		# cv2.imshow('grey',grey)

		blur = grey.copy()
		for i in range(10):
			blur = cv2.medianBlur(blur, 7)

		canny = cv2.Canny(blur, 100, 150)
		# cv2.imshow('canny',canny)

		# canny 算法识别的轮廓不连续，需要膨胀一下
		ele = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5), (2, 2))
		dilate = cv2.dilate(canny, ele)
		# cv2.imshow('dilate',dilate)

		ret, thresh = cv2.threshold(dilate, 100, 255, cv2.THRESH_BINARY_INV)
		# cv2.imshow('thresh',thresh)

		contour, points, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

		newImg = np.zeros((555, 400), np.uint8)
		newImg[...] = 255
		positions = []

		for pt in points:
			pos = self.drawCircle(pt, newImg)
			positions.append(pos)

		# 去掉最外面的轮廓
		positions.pop()
		positions.sort(key=functools.cmp_to_key(
			lambda x, y: 1 if (x[0] - y[0]) >= 1 or abs(x[0] - y[0]) < 1 and (x[1] - y[1]) >= 1 else 0 if abs(
				x[0] - y[0]) < 1 and abs(x[1] - y[1]) < 1 else -1))
		self.positions=positions

		self.cols, y_labels = self.cluster_fit([[positions[i][0], 0] for i in range(len(positions))])
		self.rows, x_labels = self.cluster_fit([[positions[i][1], 0] for i in range(len(positions))])
		# 排序后行坐标的编号可能是乱的，要修正
		x_labels = self.cluster_fix([[positions[i][1], 0] for i in range(len(positions))], x_labels)

		self.map = np.zeros((self.rows, self.cols))
		self.map[...] = config.NULL
		for i in range(len(x_labels)):
			self.map[x_labels[i], y_labels[i]] = config.EMPTY
		# print('map = ', map)

		# 寻找起点和终点
		self.mark_start_end(self.map, positions, x_labels, y_labels)
		# print('after finding, map = ', map)

		# cv2.imshow('newImg',newImg)
		# cv2.waitKey(0)
		self.coordinate2position()
		return self.map

	# 把map坐标和真实图像的坐标对应起来
	def coordinate2position(self):
		self.dict={}
		ptr=0
		for j in range(self.cols):
			for i in range(self.rows):
				if self.map[i][j]!=config.NULL:
					self.dict[(i,j)]=(int(self.positions[ptr][0]),int(self.positions[ptr][1]))
					ptr+=2
		print('dict = ',self.dict)
		pass

	# 获得最小外接圆的圆心半径
	def drawCircle(self,points, img):
		(x, y), r = cv2.minEnclosingCircle(points)
		center = (int(x), int(y))
		r = int(r)
		cv2.circle(img, center, r, (0, 0, 255), 2)
		return (x, y, r)

	# 给数据标号
	def cluster_fit(self,arr):
		db = DBSCAN(min_samples=2).fit(arr)
		labels = db.labels_
		# print('labels = ', labels)
		num = len(set(labels)) - (1 if -1 in labels else 0)
		# print('num of clusters = ', num)
		return num, labels

	# 修正标记
	def cluster_fix(self,points, labels):
		ids = labels.copy()
		id = 0
		arr = []
		for i in range(len(points)):
			if labels[i] == id:
				arr.append((points[i], len(arr)))
				id += 1
		# print('before arr = ',arr)
		arr.sort(key=lambda x: x[0][0])
		# print('after arr = ',arr)
		idmap = {}
		for i in range(len(arr)):
			idmap[arr[i][1]] = i

		for i in range(len(ids)):
			ids[i] = idmap[ids[i]]

		return ids

	# 标记地图起点和终点
	# 原本想的是度数为1的就是终点，但是某猪提醒我这不是充要条件，因此没必要找到终点
	def mark_start_end(self,map, points, x_labels, y_labels):
		min = sys.maxsize
		index = 0
		for i in range(len(points)):
			if points[i][2] < min:
				min = points[i][2]
				index = i
		map[x_labels[index]][y_labels[index]] = config.START

	# for i in range(len(map)):
	# 	for j in range(len(map[0])):
	# 		degree=0
	# 		if i-1>=0 and map[i-1][j]==config.EMPTY:
	# 			degree+=1
	# 		if i+1<len(map) and map[i+1][j]==config.EMPTY:
	# 			degree+=1
	# 		if j-1>=0 and map[i][j-1]==config.EMPTY:
	# 			degree+=1
	# 		if j+1<len(map[0]) and map[i][j+1]==config.EMPTY:
	# 			degree+=1
	# 		if degree==1:
	# 			map[i][j]=config.END
	# 			return

	def visualize_solution(self,solution, path, save=False):
		img = cv2.imread(path)
		img=cv2.resize(img,(400,600))
		img=img[45:600,0:400]

		first=self.dict[solution[0]]
		for i in range(1,len(solution)):
			second=self.dict[solution[i]]
			cv2.line(img,first,second,(0,0,255),5)
			first=second

		if save:
			cv2.imwrite('solution_'+path,img)
		cv2.imshow('solution',img)
		cv2.waitKey(0)
		pass

