from llm import generate_text
from prompts import WRITER_PROMPT
def create_post(topic,audience,platform,tone,length):
    prompt=WRITER_PROMPT.format(
        topic=topic,
        audience=audience,
        platform=platform,
        tone=tone,
        length=length
    )
    return generate_text(prompt)

if __name__=="__main__":
    post=create_post(
        topic="Study",
        audience="student",
        platform="Instagram",
        tone="Serious",
        length="Medium"
    )
    print("++++++++Generated Post++++++++++")
    print(post)