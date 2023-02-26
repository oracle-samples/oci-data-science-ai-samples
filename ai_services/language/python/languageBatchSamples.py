import oci

key1 = "doc1"
key2 = "doc2"
text1 = "The Indy Autonomous Challenge is the worlds first head-to-head, high speed autonomous race taking place at the Indianapolis Motor Speedway"
text2 = "Using high-performance GPU systems in the Oracle Cloud, OCI will be the cloud engine for the artificial intelligence models that drive the MIT Driverless cars competing in the Indy Autonomous Challenge."
text3 = "OCI ha realizado con éxito la transición de Renault para ejecutar sus cargas de trabajo de computación de alto rendimiento (HPC) de producción en OCI. Específicamente, las cargas de trabajo para Crash Simulation usando PAM-CRASH, ya han superado el rendimiento local anterior en un 19 %. Se trata de un logro importante, ya que la mejora del rendimiento permite a Renault realizar cientos de simulaciones aerodinámicas y de colisión más al año, lo que da como resultado vehículos más seguros y con un consumo de combustible más eficiente. Renault es la tercera victoria automotriz más grande para OCI, extendiendo el alcance de OCI para cubrir los tres mercados automotrices más grandes: EE. UU., APAC y EMEA."
piiText = "I am reaching out to seek help with my credit card number 1234 5678 9873 2345 expiring on 11/23. There was a suspicious transaction on 12-Aug-2022 which I reported by calling from my mobile number (423) 111-9999 also I emailed from my email id sarah.jones1234@hotmail.com. Would you please let me know the refund status?\nRegards,Sarah"

ai_client = oci.ai_language.AIServiceLanguageClient(oci.config.from_file())

compartment_id = "<Provice your compartment Id here>"

language_code = "en"

# Batch Detect Dominant Language
doc1 = oci.ai_language.models.DominantLanguageDocument(key=key1, text=text1)
doc2 = oci.ai_language.models.DominantLanguageDocument(key=key2, text=text2)
documents = [doc1, doc2]
batch_detect_dominant_language_details = oci.ai_language.models.BatchDetectDominantLanguageDetails(documents=documents,
                                                                                                   compartment_id=compartment_id)
output = ai_client.batch_detect_dominant_language(batch_detect_dominant_language_details)
print(output.data)

doc1 = oci.ai_language.models.TextDocument(key=key1, text=text1, language_code=language_code)
doc2 = oci.ai_language.models.TextDocument(key=key2, text=text3, language_code=language_code)
documents = [doc1, doc2]

# Batch Text Classification
batch_detect_language_text_classification_details = oci.ai_language.models.BatchDetectLanguageTextClassificationDetails(
    documents=documents, compartment_id=compartment_id)
output = ai_client.batch_detect_language_text_classification(batch_detect_language_text_classification_details)
print(output.data)

# Batch Named Entity Recoginiton
batch_detect_language_entities_details = oci.ai_language.models.BatchDetectLanguageEntitiesDetails(documents=documents,
                                                                                                   compartment_id=compartment_id)
output = ai_client.batch_detect_language_entities(batch_detect_language_entities_details)
print(output.data)

# Batch Key Phrase Detection
batch_detect_language_key_phrases_details = oci.ai_language.models.BatchDetectLanguageKeyPhrasesDetails(
    documents=documents, compartment_id=compartment_id)
output = ai_client.batch_detect_language_key_phrases(batch_detect_language_key_phrases_details)
print(output.data)

# Aspect based and Sentence level Sentiment Analysis
batch_detect_language_sentiment_details = oci.ai_language.models.BatchDetectLanguageSentimentsDetails(
    documents=documents, compartment_id=compartment_id)
output = ai_client.batch_detect_language_sentiments(batch_detect_language_sentiment_details,
                                                    level=["ASPECT", "SENTENCE"])
print(output.data)

# Language Translation
doc1 = oci.ai_language.models.TextDocument(key=key1, text=text1, language_code=language_code)
doc2 = oci.ai_language.models.TextDocument(key=key2, text=text2, language_code=language_code)
documents = [doc1, doc2]
batch_language_translation_details = oci.ai_language.models.BatchLanguageTranslationDetails(documents=documents,
                                                                                            compartment_id=compartment_id,
                                                                                            target_language_code="de")
output = ai_client.batch_language_translation(batch_language_translation_details)
print(output.data)

# Personal Identifiable Information
doc1 = oci.ai_language.models.TextDocument(key=key1, text=piiText, language_code=language_code)
documents = [doc1]
piiEntityMasking = oci.ai_language.models.PiiEntityMask(mode="MASK", masking_character="*")
masking = {"ALL": piiEntityMasking}
batch_detect_language_pii_entities_details = oci.ai_language.models.BatchDetectLanguagePiiEntitiesDetails(
    documents=documents, compartment_id=compartment_id, masking=masking)
output = ai_client.batch_detect_language_pii_entities(batch_detect_language_pii_entities_details)
print(output.data)
