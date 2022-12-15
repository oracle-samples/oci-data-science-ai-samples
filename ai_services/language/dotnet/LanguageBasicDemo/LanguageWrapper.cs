using Oci.AilanguageService;
using Oci.AilanguageService.Models;
using Oci.AilanguageService.Requests;
using Oci.Common;
using Oci.Common.Auth;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace LanguageBasicDemo
{
    internal class LanguageWrapper
    {
        private readonly AIServiceLanguageClient client;

        public LanguageWrapper()
        {
            // Create a default authentication provider that uses the DEFAULT
            // profile in the configuration file.
            // Refer to <see href="https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File>the public documentation</see> on how to prepare a configuration file. 
            var provider = new ConfigFileAuthenticationDetailsProvider("DEFAULT");
            client = new AIServiceLanguageClient(provider, new ClientConfiguration());
        }


        public async Task<DetectedLanguage> GetTextLanguageAsync(string text)
        {
            // Create a request and dependent object(s).
            var batchDetectDominantLanguageDetails = new BatchDetectDominantLanguageDetails
            {
                Documents = new List<DominantLanguageDocument>
                {
                    new DominantLanguageDocument
                    {
                        Key = "doc-1",
                        Text = text
                    }
                }
            };

            var batchDetectDominantLanguageRequest = new BatchDetectDominantLanguageRequest
            {
                BatchDetectDominantLanguageDetails = batchDetectDominantLanguageDetails,
                OpcRequestId = "394ZXI6MCFAHTJX1ZFSX<unique_ID>"
            };

            var response = await client.BatchDetectDominantLanguage(batchDetectDominantLanguageRequest);

            // Retrieve value from the response.
            var documentsValue = response.BatchDetectDominantLanguageResult.Documents;

            //Console.WriteLine(documentsValue[0].Languages[0].ToString());

            return documentsValue[0].Languages[0];
        }

        public async Task<string> TranslateTextAsync(string text)
        {
            // Create a request and dependent object(s).
            var batchDetails = new BatchLanguageTranslationDetails
            {
                Documents = new List<TextDocument>
                {
                    new TextDocument
                    {
                        Key = "doc-1",
                        Text = text,
                        LanguageCode = "en"
                    }
                },
                
                TargetLanguageCode = "es"
            };

            var request = new BatchLanguageTranslationRequest
            {
                BatchLanguageTranslationDetails = batchDetails,
                OpcRequestId = "394ZXI6MCFAHTJX1ZFSX<unique_ID>"
            };

            var response = await client.BatchLanguageTranslation(request);

            // Retrieve value from the response.
            var documentsValue = response.BatchLanguageTranslationResult.Documents;

            return documentsValue[0].TranslatedText;
        }

        private List<TextDocument> TextDocumentListFromString(string text, string languageCode)
        {
            return new List<TextDocument>
                {
                    new TextDocument
                    {
                        Key = "doc-1",
                        Text = text,
                        LanguageCode = languageCode
                    }
                };
        }

        public async Task<List<KeyPhrase>> GetKeyPhrasesAsync(string text)
        {
            // Create a request and dependent object(s).
            var batchDetails = new BatchDetectLanguageKeyPhrasesDetails
            {
                Documents = TextDocumentListFromString(text, "en")
            };

            var request = new BatchDetectLanguageKeyPhrasesRequest
            {
                BatchDetectLanguageKeyPhrasesDetails = batchDetails,
                OpcRequestId = "394ZXI6MCFAHTJX1ZFSX<unique_ID>"
            };

            var response = await client.BatchDetectLanguageKeyPhrases(request);

            // Retrieve value from the response.
            var documentsValue = response.BatchDetectLanguageKeyPhrasesResult.Documents;

            return documentsValue[0].KeyPhrases;
        }

        public async Task<TextClassification> ClassifyAsync(string text)
        {
            // Create a request and dependent object(s).
            var batchDetails = new BatchDetectLanguageTextClassificationDetails
            {
                Documents = TextDocumentListFromString(text, "en")
            };

            var request = new BatchDetectLanguageTextClassificationRequest
            {
                BatchDetectLanguageTextClassificationDetails = batchDetails,
                OpcRequestId = "394ZXI6MCFAHTJX1ZFSX<unique_ID>"
            };

            var response = await client.BatchDetectLanguageTextClassification(request);

            // Retrieve value from the response.
            var documentsValue = response.BatchDetectLanguageTextClassificationResult.Documents;

            return documentsValue[0].TextClassification[0];
        }

        public async Task<List<HierarchicalEntity>> GetEntitiesAsync(string text)
        {
            // Create a request and dependent object(s).
            var batchDetails = new BatchDetectLanguageEntitiesDetails
            {
                Documents = TextDocumentListFromString(text, "en")
            };

            var request = new BatchDetectLanguageEntitiesRequest
            {
                BatchDetectLanguageEntitiesDetails = batchDetails,
                OpcRequestId = "394ZXI6MCFAHTJX1ZFSX<unique_ID>"
            };

            var response = await client.BatchDetectLanguageEntities(request);

            // Retrieve value from the response.
            var documentsValue = response.BatchDetectLanguageEntitiesResult.Documents;

            return documentsValue[0].Entities;
        }

        public async Task<SentimentDocumentResult> GetSentimentAsync(string text)
        {
            // Create a request and dependent object(s).
            var batchDetails = new BatchDetectLanguageSentimentsDetails
            {
                Documents = TextDocumentListFromString(text, "en")
            };

            var request = new BatchDetectLanguageSentimentsRequest
            {
                BatchDetectLanguageSentimentsDetails = batchDetails,
                OpcRequestId = "394ZXI6MCFAHTJX1ZFSX<unique_ID>",
                Level = new List<BatchDetectLanguageSentimentsRequest.LevelEnum>()
                {  
                    BatchDetectLanguageSentimentsRequest.LevelEnum.Sentence, 
                    BatchDetectLanguageSentimentsRequest.LevelEnum.Aspect
                }
            };

            var response = await client.BatchDetectLanguageSentiments(request);

            // Retrieve value from the response.
            var result = response.BatchDetectLanguageSentimentsResult.Documents;

            return result[0];
        }

    }
}
