import json

class model:
    def predict(self,data):
        print('data received by predict function')
        #import json        
        number = None

        if isinstance(data, dict):
            number = data.get("number", None)
        elif isinstance(data, str):
            data = json.loads(data)
            number = data.get("number", None)

        print('input number is',number)

        calc = abs(number)**0.5

        return calc