from back_end.useful_functions import get_completion
import json

emotions = ["Joy", "Sadness", "Fear", "Love", "Hate", "Pride", "Shame"]


class Emotion:
    def __init__(self, agent_name):
        try:
            with open(f'back_end/memory/current_emotion.json', 'r') as file:
                data = json.load(file)
                self.stable_state = data[agent_name]["stable_state"]
        except FileNotFoundError:
            print(f"file current_emotion cannot be found")
            self.stable_state = [0, 0, 0, 0, 0, 0, 0]

        self.emotions = self.stable_state.copy()
        self.activation_thresholds = 0
        self.weakening_function = 0

    def print_emotions(self):
        '''
        INPUT: None
        OUTPUT: the current emotional state of the agent in a string format
        '''
        emotions = ["Joy", "Sadness", "Fear", "Love", "Hate",
                    "Pride", "Shame"]  # Assuming these are the emotions
        desc = ', '.join(f"{emotion} {value}" for emotion,
                         value in zip(emotions, self.emotions))
        return ("Here is its current emotional state: (0 means the emotion is not felt, 10 means it is felt to the maximum) - " + desc + ".")

    def update_emotion_resp(self, response, agent_name):
        '''
        INPUT: response, agent_name
        OUTPUT: update the emotional state of the agent after an event STEP 1
        '''

        if response == 'False':
            return False
        else:
            lines = response.split('\n')
            if len(lines) > 1:
                new_values = []
                for x in lines[1].strip('[]').split(','):
                    try:
                        new_values.append(float(x))
                    except ValueError:
                        print(f"La valeur '{x}' n'est pas un float valide.")
                if any(not 0 <= new_val <= 10 for new_val in new_values):
                    print("Values must be between 0 and 10.")
                    return False
                try:
                    with open('back_end/memory/current_emotion.json', 'r') as file:
                        data = json.load(file)
                except FileNotFoundError:
                    print(f"file current_emotion cannot be found")
                    return False
                if agent_name in data:
                    data[agent_name]["current_state"] = new_values
                else:
                    print(
                        f"Agent {agent_name} not found in current_emotion.json")
                with open('back_end/memory/current_emotion.json', 'w') as file:
                    json.dump(data, file, indent=4)
                self.emotions = new_values  # Update the current state
                print(self.print_emotions())
                return True

    def update_emotion(self, agent, event):
        '''
        INPUT: agent, event
        OUTPUT: update the emotional state of the agent after an event STEP 2
        '''
        file = open('back_end/prompts/emotion.txt', 'r')
        prompt_emotion = file.read().replace("#agent_name#", agent.name).replace("#event#", event).replace(
            "#emotionnal_state#", str(agent.print_emotions())).replace("#personality#", str(agent.print_personality()))
        file.close()
        prompt_emotion = prompt_emotion.split("###")
        message = [
            {'role': 'system',
             'content': prompt_emotion[0]},
            {'role': 'user',
             'content': prompt_emotion[1]},
        ]
        response_emotion = get_completion(
            message, max_tokens=500, temperature=0)
        self.update_emotion_resp(response_emotion, agent.name)
        return response_emotion
