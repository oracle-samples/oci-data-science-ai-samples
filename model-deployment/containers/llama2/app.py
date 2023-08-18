import os
import string
import gradio as gr
from loguru import logger
from inference import query


logger.debug("App to Use LLM on Model Deployment")

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                [],
                label=os.environ["MODEL"],
                show_label=True,
                show_share_button=True,
                height=500,
            )

        with gr.Column(scale=1, offset=0.01):
            max_tokens = gr.Slider(
                256,
                4096,
                value=256,
                step=16,
                label="max_tokens",
                info="The maximum number of tokens",
            )

            temperature = gr.Slider(
                0.2,
                2.0,
                value=1.0,
                step=0.1,
                label="temperature",
                info="Controls randomness in the model. The value is used to modulate the next token probabilities.",
            )

            top_p = gr.Slider(
                0.1,
                1.0,
                value=0.95,
                step=0.1,
                label="top_p",
                info="Nucleus sampling, only the smallest set of most probable tokens with probabilities that add up to top_p or higher are kept for generation.",
            )

    with gr.Row():
        with gr.Column(scale=3):
            msg = gr.Textbox(
                label="Prompt:",
                placeholder="What's the answer to life, the universe, and everything?",
                lines=2,
                autofocus=True,
            )

        with gr.Column(scale=1, offset=0.01):
            send = gr.Button(value="Generate", variant="primary", scale=1)
            clear = gr.Button("Clear")

    with gr.Row():
        examples = [
            "What's the answer to life, the universe, and everything?",
            "what does the control plane do in a public cloud architecture?",
            "Simplify the concept of quantum physics",
            "Write the python code and output to show randomized items of a list.",
            "Explain the plot of Gravity's Rainbow in a few sentences.",
        ]

        gr.Examples(
            examples=examples,
            inputs=msg,
        )

    with gr.Row():
        gr.HTML(
            """
                <div>
                    <center>Demo application of a Open Source Models on ODSC Model Deployment</center>
                    <center><a href='https://www.oracle.com/cloud/'>Powered by Oracle OCI</a></center>
                </div>
            """
        )

    def user(user_message, history):
        return ("", history + [[user_message, None]])

    def bot(history, max_tokens, temperature, top_p):
        llm_response = query(
            history[-1][0],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )

        history[-1][1] = llm_response

        return history

    send.click(
        user,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
        queue=False,
    ).then(bot, [chatbot, max_tokens, temperature, top_p], chatbot)

    clear.click(lambda: None, None, chatbot, queue=False)

    demo.queue()
    demo.launch()
