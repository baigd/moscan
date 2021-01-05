# 对象序列化
import pickle

def readbunchobj(path):
    file_obj = open(path, 'rb')
    bunch = pickle.load(file_obj)
    file_obj.close()
    return bunch

def writeBunchobj(path, bunchobj):
    file_obj = open(path, 'wb')
    pickle.dump(bunchobj, file_obj)
    file_obj.close()