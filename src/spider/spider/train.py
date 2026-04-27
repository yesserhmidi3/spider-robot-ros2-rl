import os
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback # Added this for the checkpoint
from spider_env import SpiderEnv # Import the class we just finished

def train():
    # 1. Create the environment
    env = SpiderEnv()

    #load model (added after testing):
    MODEL_PATH = "spider_ppo_model_latest.zip"
    # 2. Check if a saved model exists. If yes, load it. If no, create a new one.
    if os.path.exists(MODEL_PATH):
        print(f"--- SAVED MODEL FOUND! Loading {MODEL_PATH}... ---")
        # Notice we have to pass the env and tensorboard_log again so it knows where to keep writing
        model = PPO.load(MODEL_PATH, env=env, tensorboard_log="./ppo_spider_logs/")
    else:
        print("--- NO SAVED MODEL FOUND. Starting a new brain from scratch... ---")
        # 2. Define the AI Model (PPO)
        # MlpPolicy = Multi-layer Perceptron (standard neural network)
        # verbose=1 shows training progress in the terminal
        model = PPO(
            "MlpPolicy", 
            env, 
            verbose=1, 
            learning_rate=0.0003, 
            tensorboard_log="./ppo_spider_logs/"
        )
    # This will save a backup every 10,000 steps inside a folder called "models"
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path='./models/',
        name_prefix='spider_brain'
    )

    # 3. Set training duration
    # Start with 15,000 steps for a "Sanity Check" (about 15-30 mins)
    #then did 200,000 for overnight
    TIMESTEPS = 100000
    
    #print("--- STARTING TRAINING ---")
    print(f"--- STARTING OVERNIGHT RUN FOR {TIMESTEPS} STEPS ---")
    print("Checkpoints will save automatically every 10,000 steps.")
    print("Press Ctrl+C at any time to stop training and safely save the model.")
    #model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False)
    #print("--- TRAINING FINISHED ---")

    #added this so I can ctrl+c and save it
    try:
        model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, callback=checkpoint_callback) #changed reset_num_timesteps to False to continue from old timesteps and added callback for the checkpoint
        print("--- OVERNIGHT RUN FINISHED NATURALLY ---")
    except KeyboardInterrupt:
        # This catches the Ctrl+C command
        print("\n--- TRAINING INTERRUPTED BY USER! SAVING PROGRESS... ---")
    finally:

    # 4. Save the brain
        model.save("spider_ppo_model_latest")
        print("--- MODEL SAVED SUCCESSFULLY ---")
        env.close()
    
    #env.close()

if __name__ == '__main__':
    train()