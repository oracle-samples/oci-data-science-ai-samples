import os
import triton_python_backend_utils as pb_utils
from transformers import GPT2Tokenizer
import numpy as np

class TritonPythonModel:

    def initialize(self, args):
        tokenizer_dir = os.path.dirname(os.path.realpath(__file__))
        self.tokenizer = GPT2Tokenizer.from_pretrained(tokenizer_dir)

    def execute(self, requests):
        resps = []
        for request in requests:
            req = pb_utils.get_input_tensor_by_name(request, "TEXT")
            text = req.as_numpy().tolist()[0]
            print(text.decode("utf-8"), flush=True)
            tokens = self.tokenizer(text.decode("utf-8"), return_tensors="tf")
            print(tokens['input_ids'], flush=True)
            #shape = tokens.shape.as_list()
            input_ids = pb_utils.Tensor("input_ids", tokens['input_ids'].numpy().astype(np.int64))
            #atten = np.ones(shape, dtype=np.int32).tolist()
            attention_mask = pb_utils.Tensor("attention_mask", tokens['attention_mask'].numpy().astype(np.int64))
            inference_response = pb_utils.InferenceResponse(output_tensors=[input_ids, attention_mask])
            resps.append(inference_response)

        return resps


    def finalize(self):
        print("cleaning up")