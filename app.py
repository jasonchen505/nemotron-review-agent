"""Optional Gradio web UI for hosted demos. Run: python app.py (needs NEBIUS_API_KEY)."""
import os

import spaces

from review_agent import agent as agent_mod


@spaces.GPU  # required by Hugging Face ZeroGPU hosting; no-op elsewhere
def review(diff_text, test_cmd, model):
    if not diff_text.strip():
        return "Paste a unified diff first."
    try:
        result = agent_mod.run(
            diff_text,
            test_cmd=(test_cmd or "none"),
            model=model or None,
        )
    except Exception as e:  # surface errors in the UI instead of crashing
        return f"Error: {e}"
    return result["report"]


def main():
    import gradio as gr

    with gr.Blocks(title="Nemotron Review Agent") as demo:
        gr.Markdown(
            "# Nemotron Review Agent\n"
            "Code review agent powered by NVIDIA Nemotron on Nebius Token Factory.\n"
            "It reviews your diff, runs your test suite, then verifies each finding against test evidence."
        )
        diff = gr.Textbox(label="Unified diff", lines=15,
                          placeholder="Paste `git diff` output here...")
        with gr.Row():
            test_cmd = gr.Textbox(label="Test command", value="none",
                                  placeholder='auto / none / e.g. "pytest -q"')
            model = gr.Textbox(label="Model id (blank = default)", value="",
                               placeholder="nvidia/nemotron-3-super-120b-a12b")
        btn = gr.Button("Review", variant="primary")
        out = gr.Markdown(label="Report")
        btn.click(review, inputs=[diff, test_cmd, model], outputs=out)
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))


if __name__ == "__main__":
    main()
