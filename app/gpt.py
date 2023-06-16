import openai
from app.config import Config

messages = [
    {
        "role": "system",
        "content": "You are a great Trouble Report tool to summarize error information such as software, hardware, or field within reports.",
    },
    {
        "role": "user",
        "content": "I need that you response must be clear an concise for the next information no more to two sentences, and don't add formalizims only summary of the report issue that you can decide the type of issue/problem.",
    },
    {
        "role": "assistant",
        "content": "Understood! Please provide me with the information or context of the report issue, and I will respond with a clear and concise summary, limited to two sentences and without formalities.",
    },
    {
        "role": "user",
        "content": "If your input seems like: I'm experiencing a issue with my Kiwibot at location New York. The issue is related to the wheels not moving properly. I noticed this problem when the bot was attempting to navigate uneven surfaces. The wheels seem to get stuck frequently. Response some like the next: The Kiwibot at our NY location is experiencing a hardware(choice) problem with the wheels, causing frequent sticking and hindering its mobility, especially on uneven surfaces.",
    },
    {
        "role": "assistant",
        "content": "The Kiwibot in New York is facing a hardware issue with the wheels, resulting in frequent sticking and limited mobility, particularly on uneven surfaces.",
    },
    {
        "role": "user",
        "content": "From any type of report you receive, make a decision on the type of problem hardware, software or field if you can't decide take undefined with the report information such as reporting battery level, robot reboot, overheating, camera failure, any movement of people nearby, o whatever other problem you consider appear.You receive:Any problem report does not need to say issue/ problem as we talked about before.Your response should be:Approve any possible human error in the input, always taking the decision of the issue/problem.",
    },
    {
        "role": "assistant",
        "content": "Based on the report information provided, here are the decisions on the type of problem:Battery level low, Kiwibot unable to operate: Hardware (battery) problem.Robot unexpectedly rebooted during operation: Software problem.Kiwibot overheating, emitting smoke: Hardware problem (overheating).Camera malfunctioning, unable to capture images: Hardware problem (camera failure).Kiwibot unable to move due to obstruction by people nearby: Field problem (obstruction).Robot unable to navigate properly on uneven surfaces, wheels getting stuck: Hardware problem (wheel malfunction).Sensor failure, Kiwibot unable to detect obstacles: Hardware problem (sensor failure).Please note that these decisions are made based on the information provided, and there might be additional factors or context that could influence the actual determination of the issue/problem.",
    },
    # {
    #     "role": "user",
    #     "content": "If you recieve a <*NOTE*: Reason> at the end of the prompt, could you return the summary, and additionaly check the reason at the note and please bring a possible solution for example: call the technique service soon.",
    # },
]


class GPT:
    _instance = None
    openai.api_key = Config.OPEN_API_KEY

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GPT()
        return cls._instance

    def __init__(self):
        self.context = messages

    def generate_response(self, message):
        self.context.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.context
        )
        self.context.append(
            {
                "role": "assistant",
                "content": response["choices"][0]["message"]["content"],
            }
        )
        return response["choices"][0]["message"]["content"]
