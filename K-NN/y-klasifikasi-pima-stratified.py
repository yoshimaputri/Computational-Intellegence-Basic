import csv
import math
import operator
import numpy as np
from sklearn.model_selection import StratifiedKFold

def normalize(data):
	for i in range(len(data[1]) - 1):
		arr = []
		for x in data:
			arr.append(x[i])
		for x in data:
			x[i] = (x[i] - np.min(arr)) / (np.max(arr) - np.min(arr)) 
	return data

def loadDataset(filename, p, split, trainSet=[] , testSet=[]):
	with open(filename, 'r') as csvfile:
		lines = csv.reader(csvfile)
		dataset = list(lines)
		np.random.shuffle(dataset)
		dataset = np.array(dataset).astype(np.float)
		dataset = normalize(dataset)
		return dataset

# Euclidean
def euclideanDistance(instance1, instance2, length):
	distance = 0
	for x in range(length):
		distance += pow((instance1[x] - instance2[x]), 2)
	return math.sqrt(distance)
	
# Manhattan
def manhattanDistance(p1, p2, length):
	distance = 0
	for x in range(length):
		distance += abs(p1[x] - p2[x])
	return distance

# Minkowski (r>=3)
def minkowskiDistance(p1, p2, length, r):
	distance = 0
	for x in range(length):
		distance += pow((p1[x] - p2[x]), r)
	dis = distance**(1/float(r))
	return dis.real

# Cosine
def cosineSimilarity(vector_1, vector_2, length):
	sumv1, sumv2, sumv1v2 = 0, 0, 0
	for i in range(length):
		x = vector_1[i]
		y = vector_2[i]
		sumv1 += pow(x,2)
		sumv2 += pow(y,2)
		sumv1v2 += x * y
	return 1 - (sumv1v2 / (math.sqrt(sumv1) * math.sqrt(sumv2)))

def getNeighbors(trainSet, testInstance, k, sim):
	distances = []
	r = 3
	length = len(testInstance)-1
	for x in range(len(trainSet)):
		if sim == 1:
			dist = euclideanDistance(testInstance, trainSet[x], length)
		elif sim == 2:
			dist = manhattanDistance(testInstance, trainSet[x], length)
		elif sim == 3:
			dist = minkowskiDistance(testInstance, trainSet[x], length, r)
		elif sim == 4:
			dist = cosineSimilarity(testInstance, trainSet[x], length)
		else:
			"Number of distance choosen doesn't exist"
		distances.append((trainSet[x], dist))
	distances.sort(key=operator.itemgetter(1))
	neighbors = []
	for x in range(k):
		neighbors.append(distances[x][0])
	return neighbors
 
def getResponse(neighbors):
	classVotes = {}
	for x in range(len(neighbors)):
		response = neighbors[x][-1]
		if response in classVotes:
			classVotes[response] += 1
		else:
			classVotes[response] = 1
	sortedVotes = sorted(classVotes.items(), key=operator.itemgetter(1), reverse=True)
	return sortedVotes[0][0]
 
def getAccuracy(testSet, predictions):
	correct = 0
	for x in range(len(testSet)):
		if testSet[x][-1] == predictions[x]:
			correct += 1
	return (correct/float(len(testSet))) * 100.0
	
def main():
	final = 0
	p = 0
	# fold = 10
	fold = int(input("Enter the k-fold : "))
	split = 768/fold
	#print('split',split)
	k = int(input("Enter the numbers of k-neighbors : "))
	print("\nSimilarity \n1. Euclidean Distance\n2. Manhattan/ City Block\n3. Minkowski Distance\n4. Cosine Similarity")
	sim = int(input("Choose the number according to the Similarity Method : "))
	if sim == 3:
		r = int(input('Enter the number of r : '))

	trainSet=[]
	testSet=[]
	dataset = loadDataset('pima-indians-diabetes.data', p, split, trainSet, testSet)
	print(dataset.shape)
	x = dataset[:, :-1]
	y = dataset[:, -1]
	skf = StratifiedKFold(n_splits=fold, shuffle=True)
	i = 0

	for train, test in skf.split(x,y):
		trainSet = dataset[train]
		testSet = dataset[test]
		print ('---')
		print ('Train set: ' + repr(len(trainSet)))
		print ('Test set: ' + repr(len(testSet)))
		predictions=[]
		#print(k, type(k))
		for x in range(len(testSet)):
			neighbors = getNeighbors(trainSet, testSet[x], k, sim)
			result = getResponse(neighbors)
			predictions.append(result)
			#print('|>| predicted=' + repr(result) + ', actual=' + repr(testSet[x][-1]))
		accuracy = getAccuracy(testSet, predictions)
		print('Accuracy Fold['+ str(i+1) + ']: ' + repr(accuracy) + ' %')
		final+=accuracy
		p+=split
		i+=1
	finalacc = final / fold #rata" akurasi
	print()
	print('Final Accuracy: ' + str(finalacc) + ' %')
	
main()