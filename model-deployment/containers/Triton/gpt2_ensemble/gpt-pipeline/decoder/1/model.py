import json
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
            req = pb_utils.get_input_tensor_by_name(request, "logits")
            print(req, flush=True)

            next_token = req.as_numpy().argmax(axis=2)[0]
            next_token_str = self.tokenizer.decode(
                next_token[-1:], skip_special_tokens=True, clean_up_tokenization_spaces=True
            ).strip()

            print("next str", next_token_str, flush=True)

            response = pb_utils.Tensor("out", np.array([next_token_str], dtype=object))
            inference_response = pb_utils.InferenceResponse(output_tensors=[response])
            resps.append(inference_response)

        return resps


    def finalize(self):
        print("cleaning up")