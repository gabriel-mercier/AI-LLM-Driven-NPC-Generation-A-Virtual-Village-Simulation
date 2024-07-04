# AI-LLM-Driven NPC Generation: A Virtual Village Simulation

This project explores the use of artificial intelligence to generate realistic non-player characters (NPCs) in a virtual village environment. The NPCs are designed to interact autonomously, creating a dynamic and immersive simulation.

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

- Zakaria Abboud
- Gabriel Mercier
- Yingwei Tang
- Brahim Touayouch
- Siyuan Zou

## License

This project is licensed under the MIT License.
