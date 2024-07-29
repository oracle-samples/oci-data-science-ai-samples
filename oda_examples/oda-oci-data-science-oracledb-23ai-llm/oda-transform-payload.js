'use strict';

// Documentation for writing LLM Transformation handlers: https://github.com/oracle/bots-node-sdk/blob/master/LLM_TRANSFORMATION_HANDLER.md

// You can use your favorite http client package to make REST calls, however, the node fetch API is pre-installed with the bots-node-sdk.
// Documentation can be found at https://www.npmjs.com/package/node-fetch
// Un-comment the next line if you want to make REST calls using node-fetch.
// const fetch = require("node-fetch");

module.exports = {
  metadata: {
    name: 'oci_md_handler',
    eventHandlerType: 'LlmTransformation'
  },
  handlers: {

    /**
    * Handler to transform the request payload
    * @param {TransformPayloadEvent} event - event object contains the following properties:
    * - payload: the request payload object
    * @param {LlmTransformationContext} context - see https://oracle.github.io/bots-node-sdk/LlmTransformationContext.html
    * @returns {object} the transformed request payload
    */
    transformRequestPayload: async (event, context) => {
      return { "query": event.payload.messages[event.payload.messages.length - 1].content };
    },

    /**
    * Handler to transform the response payload
    * @param {TransformPayloadEvent} event - event object contains the following properties:
    * - payload: the response payload object
    * @param {LlmTransformationContext} context - see https://oracle.github.io/bots-node-sdk/LlmTransformationContext.html
    * @returns {object} the transformed response payload
    */
    transformResponsePayload: async (event, context) => {
      return { candidates: [{ "content": event.payload.prediction || "" }]};
    },

    /**
    * Handler to transform the error response payload, invoked when HTTP status code is 400 or higher and the error
    * response body received is a JSON object
    * @param {TransformPayloadEvent} event - event object contains the following properties:
    * - payload: the error response payload object
    * @param {LlmTransformationContext} context - see https://oracle.github.io/bots-node-sdk/LlmTransformationContext.html
    * @returns {object} the transformed error response payload
    */
    transformErrorResponsePayload: async (event, context) => {
     let errorCode = 'unknown';
     if (event.payload.error) {
        if ( 'context_length_exceeded' === event.payload.error.code) {
            errorCode = 'modelLengthExceeded'; }
        else if ('content_filter' === event.payload.error.code) {
            errorCode = 'flagged';
        }
        return {"errorCode" : errorCode, "errorMessage": event.payload.error.message};
     }
     return {"errorCode" : errorCode, "errorMessage": JSON.stringify(event.payload)};

    }
  }
};
