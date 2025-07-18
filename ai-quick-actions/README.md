# AI Quick Actions

AI Quick Actions is a suite of actions that together can be used to deploy, evaluate and fine tune open source large language models.

> **Note:** AI Quick Actions is a feature of the OCI Data Science service, that can be used within the Notebook session. To enable AI Quick Actions, you can either start a new Notebook session or deactivate and reactivate any existing ones. Once enabled, the AI Quick Actions icon will appear in the Extensions section of the launcher.
>
>![AQUA](web_assets/aqua.png)
>
>Before you can use AI Quick Actions (referred to as AQUA) you will need to apply the necessary policies either using the Oracle Resource
Manager (ORM) or manually. For further information see [Policies](policies/README.md).

---
- [Release Notes](release-notes.md)
- [Policies](policies/README.md)
- [Troubleshooting Tips](troubleshooting-tips.md)
- [Supported Container List](ai-quick-actions-containers.md)
- [Supported GPU Shape List](supported-gpu-shapes.md)
- [Model Deployment](model-deployment-tips.md)
- [MultiModel Deployment](multimodel-deployment-tips.md)
- [Model Deployment Private Endpoint](model-deployment-private-endpoint-tips.md)
- [Model Fine Tuning](fine-tuning-tips.md)
- [Model Evaluation](evaluation-tips.md)
- [Model Registration](register-tips.md)
- [MultiModal Models Tips](multimodal-models-tips.md)
- [Time Series Forecasting](time-series-forecasting/README.md)
- [CLI](cli-tips.md)


## Use Case Example

Looking at a general use case, this is how AQUA would help. You're a marketing executive and you need to write
success stories for your company blog. Right now you interview customers and from the transcripts create blog posts
that showcase a particular style and narrative that supports your business goals. For example you may want to
emphasize the cost savings, or the competitive advantage, or some aspect. You may also want to generate blogs in
other languages.

### Where do you start?

AQUA first introduces you to a model catalog. The models found here are ones that Oracle have tested, remember
these are open source models - unmodified by Oracle - each will have strengths and weaknesses and suitability for
different tasks. As of Spring 2024 the model that covers a reasonable selection of languages, works well for a
variety of tasks, is capable of being responsible, and responds well to instructions is
the [Mistral model](https://mistral.ai/technology/#models) - this comes in different flavors/sizes.

### Step One would be to deploy a model using the Model Explorer

![AQUA](web_assets/model-explorer.png)

Read the model cards for more information that can help you select a suitable model. One common need is to evaluate a few models against a small set of examples. Then see which model
best aligns with the use case. To do this you will need to create an evaluation dataset. See [here](evaluation-tips.md) for
more information and tips.

It could be that after evaluating a few service models either they work great for your use case, or none of them work
well enough. If you find none of them work as expected you have a number of options available to you.

- explore better prompt templates
- fine tune a model

Prompt templates are easy to play with, fine tuning is a more advanced topic, to make use of fine tuning you teach the model
how you want it to respond through a set of examples.

For example rather than a simple prompt template like:

> You are a helpful assistant

try something task-specific. For our
use case you could re-run the evaluation with a template like:

> Please respond to me as a marketing writer. My company makes \<insert\>, You will help me writing a customer success story.
> Avoid jargon, be objective, incorporate quotations, give background information, keep it short, be accurate.

Prompt templates are very powerful, models respond well to being instructed to follow direction. For example a prompt that
does well to minimize bias and hallucinations try something like:

>
> \<s\>[INST] \<\<SYS\>\>
> You are an expert, give helpful, detailed, accurate responses, don't use fluffy phrases like "thank you", "Certainly", or "Hello!". Your answers
>
> should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially
> unbiased and positive in nature.
>
> Format any code or configuration properly with appropriate indentation and surround with markdown code blocks.
>
> Do not write sign-off messages, do not say hello, do not say thank you, do not say goodbye, do not say anything that is not directly related to the question.
>
> If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If > you don't know the answer to a question, please don't share false information.
>
> \<\</SYS\>\>
>
> \<my question/promp\> [/INST]

Use the "Test Your Model" feature in the UI to try a variety of prompts to see if the model is working as expected.

![AQUA](web_assets/try-model.png)

See [sampling parameters](https://docs.vllm.ai/en/latest/dev/sampling_params.html) for an explanation of all the parameters you can tune your model with.

- *temperature* is very important. It is a parameter that influences the large language model's output, determining
whether the output is more random and creative or more predictable. A higher temperature value will influence the model
to select more randomly from the possible outputs therefore introducing more creativity in the result.

- *max_tokens* The maximum size of the output. Increase to get longer responses from the model.

In some cases a more sophisticated solution is needed, for example [fine tuning.](fine-tuning-tips.md)


- [Release Notes](release-notes.md)
- [Policies](policies/README.md)
- [Troubleshooting Tips](troubleshooting-tips.md)
- [Supported Container List](ai-quick-actions-containers.md)
- [Supported GPU Shape List](supported-gpu-shapes.md)
- [Model Deployment](model-deployment-tips.md)
- [MultiModel Deployment](multimodel-deployment-tips.md)
- [Model Deployment Private Endpoint](model-deployment-private-endpoint-tips.md)
- [Model Fine Tuning](fine-tuning-tips.md)
- [Model Evaluation](evaluation-tips.md)
- [Model Registration](register-tips.md)
- [MultiModal Models Tips](multimodal-models-tips.md)
- [Time Series Forecasting](time-series-forecasting/README.md)
- [CLI](cli-tips.md)

