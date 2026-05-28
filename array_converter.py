import numpy as np
import csv as csv


# test array of random large depth values in meters
test_array = np.array([
    [2.5, 3.0, 4.0],
    [1.5, 2.0, 3.0],
    [0.5, 1.0, 200]
])

class ArrayConverter:
    def __init__(self, array):
        self.array = array
    
    mapping = {
    'empty': 0,
    'object_far': 1,
    'object_close': 2
    }

    def getThreshold(self, array):
        threshold = np.mean(array) + np.std(array)
        return threshold/2


    def data_convert(self, array):
        threshold = self.getThreshold(array)
        arr_size = array.shape
        converted_array = np.zeros(arr_size)

        for i in range(len(array)):
            for j in range(len(array[i])):
                distance = array[i][j]
                if distance > threshold:
                    converted_array[i][j] = self.mapping['empty']
                    #return self.mapping['empty']
                elif distance > threshold / 2:
                    converted_array[i][j] = self.mapping['object_far']
                    #return self.mapping['object_far']
                else:
                    converted_array[i][j] = self.mapping['object_close']
                    #return self.mapping['object_close']

        return converted_array
    
    def arrayToCSV(self, array, filename='output.csv'):
        array = self.data_convert(array)
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in np.array(array):
                writer.writerow(row)


converter = ArrayConverter(test_array)
converter.arrayToCSV(test_array, 'output.csv')

opened_file = open('output.csv', mode='r')
reader = csv.reader(opened_file)

