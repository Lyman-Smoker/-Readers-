'''

A12 文件，该文件是 1个LSTM层+2个dense层 的主结构文件
并用于训练IPN数据集，产生预训练模型

'''

import tensorflow as tf
from tensorflow.keras.layers import Input,Dense,LSTM,Lambda,BatchNormalization
import tensorflow.keras.backend as K
from tensorflow.keras.models import Model
from read_npy_file_process import read_dataset_and_process


path_train_data_x_IPN = 'A12data/train_data.npy'
path_train_data_y_IPN = 'A12data/train_data_y.npy'
x1,x2,train_data_y = read_dataset_and_process(path_train_data_x_IPN,path_train_data_y_IPN)



# 构建孪生网络主结构类
class my_lstm:
    def __init__(self):
        self.block1 = LSTM(units=21, return_sequences=False)
        self.block2 = BatchNormalization()

    def call(self, inputs):
        x = inputs
        x = self.block1(x)
        x = self.block2(x)
        return x

    pass


# 构建孪生网络主结构
def siamesenet(input_shape):
    my_modellstm = my_lstm()

    input1 = Input(shape=input_shape)
    input2 = Input(shape=input_shape)

    i1 = my_modellstm.call(input1)
    i2 = my_modellstm.call(input2)

    l1_distance_layer = Lambda(
        lambda tensor: K.abs(tensor[0] - tensor[1])
    )
    l1_distance = l1_distance_layer([i1, i2])

    out1 = Dense(10, activation='relu')(l1_distance)
    out = Dense(1, activation='sigmoid')(out1)

    model = Model([input1, input2], out)
    return model


#得到一个实例化的孪生网络
final = siamesenet([60,21])


def lossf_3(y_true,y_pred):
    return K.mean((1-y_true) * K.square(y_pred) + (y_true)*K.square(K.maximum(1-y_pred,0)))


final.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
              loss=lossf_3
          )






#训练模型
final.fit([x1,x2] , train_data_y , batch_size=128 , verbose=1,epochs=250)
final.summary()


#保存预训练出的神经网络模型
path = 'D:/CNNbkuniversity/compare_model/1LSTM_2DENSE/1lstm_2dense.h5'
final.save(path)

