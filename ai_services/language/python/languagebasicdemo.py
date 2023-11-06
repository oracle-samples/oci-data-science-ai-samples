import oci

text = "Zoom interface is really simple and easy to use. The learning curve is very short thanks to the interface. It is very easy to share the Zoom link to join the video conference. Screen sharing quality is just ok. Zoom now claims to have 300 million meeting participants per day. It chose Oracle Corporation co-founded by Larry Ellison and headquartered in Redwood Shores , for its cloud infrastructure deployments over the likes of Amazon, Microsoft, Google, and even IBM to build an enterprise grade experience for its product. The security feature is significantly lacking as it allows people to zoom bomb"

#Create Language service client with user config default values. Please follow below link to setup ~/.oci directory and user config
#https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm
#https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/configuration.html

ai_client = oci.ai_language.AIServiceLanguageClient(oci.config.from_file())

#Detect Entities
detect_language_entities_details = oci.ai_language.models.DetectLanguageEntitiesDetails(text=text)
output = ai_client.detect_language_entities(detect_language_entities_details)
print(output.data)

#Detect Language
detect_dominant_language_details = oci.ai_language.models.DetectDominantLanguageDetails(text=text)
output = ai_client.detect_dominant_language(detect_dominant_language_details)
print(output.data)

#Detect KeyPhrases
detect_language_key_phrases_details = oci.ai_language.models.DetectLanguageKeyPhrasesDetails(text=text)
output = ai_client.detect_language_key_phrases(detect_language_key_phrases_details)
print(output.data)

#Detect Sentiment
detect_language_sentiments_details = oci.ai_language.models.DetectLanguageSentimentsDetails(text=text)
output = ai_client.detect_language_sentiments(detect_language_sentiments_details)
print(output.data)

#Detect Text Classification
detect_language_text_classification_details = oci.ai_language.models.DetectLanguageTextClassificationDetails(text=text)
output = ai_client.detect_language_text_classification(detect_language_text_classification_details)
print(output.data)