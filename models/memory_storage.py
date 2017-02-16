from models.prediction import Prediction


class MemoryStorage:
    predictions = []

    def insert_prediction(self, prediction: Prediction):
        exists = False
        for memory in self.predictions:
            if memory.hash == prediction.hash:
                exists = True
                break

        if not exists:
            self.predictions.append(prediction)

    def yield_expired_predictions(self, ts):
        pass
