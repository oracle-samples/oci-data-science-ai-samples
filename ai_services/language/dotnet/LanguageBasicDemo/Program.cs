/******************************************************************
 * 
 *   This sample demonstrates how to issue calls to the OCI Language
 *   services from a .Net application.
 *
 *   Pre-requisites:
 *   Make sure you have created a configuration file with your credentials.
 *   See https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File
 *   for detailed instructions.  The Language class constructor in Language.cs reads that configuration file.
 *   
 *   Packages required: (You can install using the Nuget package manager)
 *     OCI.DotNetSDK.Common
 *     OCI.DotNetSDK.Ailanguage
 *     
 *   Files:
 *   LanguageWrapper.cs is a wrapper on top of the OCI Language APIs that simplifies the use of the OCI Language SDK.
 *   If you want more control over the API you may want to use the OCI Language SDK instead of the wrapper, for
 *   example if you want to use batching capabilities.
 * 
 * *****************************************************************/

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Oci.AilanguageService.Models;

namespace LanguageBasicDemo
{
    internal class Program
    {
        public static async Task Main(string[] args)
        {
            // The text to analyze.
            string textToAnalyze = "On Tuesday Jan 20 I met Bob Smith at Central Park. I like that he is a very prepared professional that should " +
                                   "be able to help me with my financial services. He is familiar with the latest IRS codes, which is a big plus. " +
                                   "That said, the cost of the service is too expensive for our current needs.";


            Console.WriteLine("Text to analyze: \n" + textToAnalyze +"\n");
            LanguageWrapper langInstance = new LanguageWrapper();


            // Detect Dominant Language
            DetectedLanguage language = await langInstance.GetTextLanguageAsync(textToAnalyze);
            Console.WriteLine("\nLanguage: \n\t" + language);

            // Classify the text 
            var textclass = await langInstance.ClassifyAsync(textToAnalyze);
            Console.WriteLine("\nText classification: \n\t {0} ({1:P2}) ", textclass.Label, textclass.Score);

            // Extract key-phrases
            List<KeyPhrase> keyphrases = await langInstance.GetKeyPhrasesAsync(textToAnalyze);
            if (keyphrases != null)
            {
                Console.WriteLine("\nKey phrases: ");
                foreach (KeyPhrase keyphrase in keyphrases)
                {
                    Console.WriteLine("\t{0} ({1:P2}) ", keyphrase.Text, keyphrase.Score);
                }
            }
            Console.WriteLine();

            // Extract Named Entities
            List<HierarchicalEntity> entities = await langInstance.GetEntitiesAsync(textToAnalyze);
            if (entities != null)
            {
                Console.WriteLine("\nEntities: ");
                foreach (HierarchicalEntity entity in entities)
                {
                    Console.WriteLine("\t{0} \tType: {1} ({1:P2})   \tOffset: {2}, \tLength: {3}", entity.Text, entity.Type, entity.Score, entity.Offset, entity.Length);
                }
            }

            // Perform sentiment analysis
            var sentimentResult = await langInstance.GetSentimentAsync(textToAnalyze);
            Console.WriteLine("\nDocument sentiment: " + sentimentResult.DocumentSentiment);

            if (sentimentResult.Aspects != null)
            {
                Console.WriteLine("\n\tAspects: ");
                foreach (var aspect in sentimentResult.Aspects)
                {
                    Console.WriteLine("\t{0} \tType: {1} ({1:P2})   \tOffset: {2}, \tLength: {3}", aspect.Text, aspect.Sentiment, aspect.Offset, aspect.Length);
                }
            }

            if (sentimentResult.Sentences != null)
            {
                Console.WriteLine("\n\tSentences: ");
                foreach (var sentence in sentimentResult.Sentences)
                {
                    Console.WriteLine("\t{0} \tType: {1} ({1:P2}) ", sentence.Text, sentence.Sentiment);
                }
            }

            // Perform translation
            var translatedText = await langInstance.TranslateTextAsync(textToAnalyze);
            Console.WriteLine("\nTranslated text: \n\t" + translatedText);
        }

    }
}
