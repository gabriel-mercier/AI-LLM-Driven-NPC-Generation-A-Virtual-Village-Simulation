# AI-LLM-Driven NPC Generation: A Virtual Village Simulation

This project explores the intersection of artificial intelligence, neuroscience, and game development by creating a virtual village populated with realistic non-player characters (NPCs). Leveraging advanced large language models (LLMs) like GPT-3.5-turbo, we generate NPCs that can autonomously interact and simulate human-like behaviors. The project employs techniques in prompt engineering to fine-tune the interactions and decision-making processes of these agents.

Our architecture is divided into a back-end and a front-end. The back-end handles the logic for NPC behavior, including memory management, emotional responses, and interaction dynamics. This is heavily inspired by principles of neuroscience to create a believable and immersive experience. The front-end, developed using Pygame and Tiled, visualizes the village and the interactions of the NPCs in real-time.

The project also explores the potential of open-source models like LLama and Mistral for enhancing NPC behavior and interaction. By integrating these models, we aim to push the boundaries of what is possible in game development, creating a rich, dynamic environment that evolves based on the actions and interactions of its inhabitants.


![thevillage](images/TheVillage.gif)

<p align="center">
  <img src="images/npc.png" alt="Image 1" width="400"/>
  <img src="images/fps.png" alt="Image 2" width="400"/>
</p>

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/gitgab22/AI-LLM-Driven-NPC-Generation.git
    cd AI-Driven-NPC-Generation
    ```
    
2. **Activate the virtual environment:**

    ```sh
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```
    
4. **Create a `.env` file in the `back_end` directory with your OpenAI API key:**

    ```sh
    echo "OPENAI_API_KEY=yourkey" > back_end/.env
    ```

## Usage

1. **Run the simulation:**

    ```sh
    python main.py
    ```

## Contributors

- Zakaria A.
- Yingwei T.
- Brahim T.
- Siyuan Z.
