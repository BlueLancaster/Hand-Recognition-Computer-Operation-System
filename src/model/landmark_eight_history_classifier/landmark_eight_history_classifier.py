import numpy as np
import tensorflow as tf
from keras.models import load_model


class LandmarkEightHistoryClassifier(object):
    def __init__(
            self,
            model_path='model/landmark_eight_history_classifier/landmark_eight_history_classifier.tflite',
            score_th=0.5,
            invalid_value=0,
            num_threads=1,
    ):
        """
        model = load_model(model_path)
        self.probability_model = model
        """
        self.interpreter = tf.lite.Interpreter(model_path=model_path,
                                               num_threads=num_threads)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.score_th = score_th
        self.invalid_value = invalid_value

    def __call__(
            self,
            point_history,
    ):
        """
        predictions = self.probability_model.predict(np.array([point_history], dtype=np.float32))
        score = tf.nn.softmax(predictions[0])
        print(np.argmax(score))
        return np.argmax(np.argmax(score))
        """

        input_details_tensor_index = self.input_details[0]['index']
        self.interpreter.set_tensor(
            input_details_tensor_index,
            np.array([point_history], dtype=np.float32))
        self.interpreter.invoke()

        output_details_tensor_index = self.output_details[0]['index']

        result = self.interpreter.get_tensor(output_details_tensor_index)

        result_index = np.argmax(np.squeeze(result))

        """
        if np.squeeze(result)[result_index] < self.score_th:
            result_index = self.invalid_value
        """
        return result_index


