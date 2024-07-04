from back_end.useful_functions import get_completion
import json

personnality_explanation = "It is an array of size 5, and each element corresponds, in order, to the following characteristics: Neuroticism, Extraversion, Openness, Agreeableness, Conscientiousness with values ranging from 0 to 10.",


class Personality:
    def __init__(self, agent_name):
        try:
            with open(f'back_end/memory/personnality.json', 'r') as file:
                data = json.load(file)
                self.personnality = data[agent_name]["beginning_state"]
        except FileNotFoundError:
            print(f"file personnality cannot be found")
            self.personnality = [0, 0, 0, 0, 0, 0, 0]

        self.history = {"Neuroticism": [self.personnality[0]],
                        "Extraversion": [self.personnality[1]],
                        "Openness": [self.personnality[2]],
                        "Agreeableness": [self.personnality[3]],
                        "Conscientiousness": [self.personnality[4]]}

    def print_personality(self):
        '''
        INPUT: None
        OUTPUT: the current personality of the agent in a string format
        '''
        personnalities = ["Neuroticism", "Extraversion",
                          "Openness", "Agreeableness", "Conscientiousness"]
        desc = ', '.join(f"{personnality} {value}" for personnality, value in zip(
            personnalities, self.personnality))
        return ("According to the Big Five, here is they current personality: (0 means the personality trait is not present, 1O means it is strongly present) - " + desc + ".")

    def update_personality_resp(self, response, agent_name):
        '''
        INPUT: response, agent_name
        OUTPUT: update the personality of the agent after an event STEP 1
        '''
        if response == 'False':
            return False
        else:
            lines = response.split('\n')
            if len(lines) > 1:
                new_values = [float(x)
                              for x in lines[1].strip('[]').split(',')]
                if any(not 0 <= new_val <= 10 for new_val in new_values):
                    print("Values must be between 0 and 10.")
                    return False
                try:
                    with open('back_end/memory/personnality.json', 'r') as file:
                        data = json.load(file)
                except FileNotFoundError:
                    print(f"file personnality cannot be found")
                    return False
                if agent_name in data:
                    data[agent_name]["current_state"] = new_values
                    data[agent_name]["history"].append(new_values)
                else:
                    print(
                        f"Agent {agent_name} not found in current_emotion.json")
                with open('back_end/memory/personnality.json', 'w') as file:
                    json.dump(data, file, indent=4)
                    self.personnality = new_values
                return True

    def update_personality(self, agent, event):
        '''
        INPUT: agent, event
        OUTPUT: update the personality of the agent after an event STEP 2
        '''
        prompt_personality = f"I am trying to model the personality of a NPC named {agent.name} from a video game. Here's the event that just happened in the life of this NPC: {event}"+agent.emotion.print_emotions()+agent.personality.print_personality(
        )+"Should we change the personality? If no, simply respond with False. If yes, modify the emotion values I provided above and give them to me in the following format, separated by &&:\n&&\nTrue\nt\n&&\n, where t is a Python array of size 5, and each element corresponds, in order, to the following characteristics: Neuroticism, Extraversion, Openness, Agreeableness, Conscientiousness with values ranging from 0 to 1."

        message_personality = [
            {'role': 'system', 'content': prompt_personality}]

        response_personality = get_completion(
            message_personality, model="gpt-3.5-turbo", max_tokens=500, temperature=0)
        self.update_personality_resp(response_personality, agent.name)

        return response_personality
