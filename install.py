import launch

if not launch.is_installed("gradio"):
    launch.run_pip("install gradio", "gradio requirement for Tag Enhancer extension")
