# Customer Review Analysis

## Goal
Create a Notebook to conduct sentiment analysis on customer writen reviews for a hotel chain utilizing pre-trained OCI AI-Language Service and then visualize the outputs to generate business insights.

## Introduction
"Customer Review Analysis" is a process of analyzing customer reviews, which are written feedback given by customers about a product or service they have used. The goal of customer review analysis is to understand the opinions and perceptions of customers about the product or service, and identify any patterns or trends that may exist. This information can be used to improve the product or service and increase customer satisfaction.

The analysis is usually done by using Natural Language Processing (NLP) techniques to extract insights, sentiment analysis to identify the overall sentiment of the reviews, and text classification to identify the main topics of reviews. The insights gained from customer review analysis can be used to improve product design, pricing, marketing, and customer service.

### What is AI-Language Services?
OCI Language Service provides suite of services to distill a deeper understanding of opinions with sentiment analysis, identify key phrases and extract named entities such as people, places and organizations to understand common subjects and patterns. You can use out of the box pre-trained models and also customize the models to suite a specific domain. OCI Language Service key features:

1. __Pre-Trained Models:__ OCI Language pre-trained APIs uses AI models trained for most common use cases.
    1. Sentiment Analysis: Identifies sentiment at the document, sentence and aspect level.
    2. Named Entity Recognition: Identifies common entities, people, places, locations, email, and so on.
    3. Key Phrase Extraction: Identify the most salient talking points in your text.
    4. Language Detection: Detects languages based on the given text, and includes a confidence score.
    4. Text Classification: Identifies the document category and subcategory that the text belongs to.
2. __Custom Models:__ OCI Language custom models enables you to customize Text Classification and Named Entity Recognition with your own data
    1. Custom Text Classification: Enables you to build a custom AI model to automatically classify text into a set of classes you pre-define, both single label and multi-label custom text classification is supported.
    2. Custom Named Entity Recognition: Enables you to build a model to identify domain-specific entities that are unique to your business or industry vertical.
3. __Text Translation:__ OCI Language now provides an API to automatically translate text across 21 languages.

### __In this notebook we are using pre-trained models for sentiment analysis (1.1 in the list above).__

### How to customize this notebook?
Instructions for using your own dataset with the customer review sentiment analysis notebook:

1. Make sure your dataset is in a format that can be read by pandas, such as a CSV or Excel file.
2. Open the notebook and navigate to the section where the dataset is loaded.
3. Replace the filename and path with the location of your own dataset.
4. Check that your dataset contains the following columns. These columns are necessary for the sentiment analysis to work. 
   1. A column to store IDs e.g. 'review_id' and,
   2. A column to store texts e.g.'review_text'.
5. If you have changed the column names in your dataset, you will need to update the column names in the notebook as well. You can do this by modifying the relevant code sections that reference those column names.
6. Note that some visualizations in the notebook may not work properly if certain columns are missing or the column names do not match. You may need to modify the code to fit your dataset's column structure.

That's it! With these steps, you should be able to use your own dataset with the customer review sentiment analysis notebook. If you have any questions or issues, feel free to reach out for help.





