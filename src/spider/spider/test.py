import time
from stable_baselines3 import PPO
from spider_env import SpiderEnv

def test():
    # 1. Start the environment
    env = SpiderEnv()
    
    # 2. Load the trained brain
    print("--- LOADING TRAINED MODEL ---")
    MODEL_PATH = "spider_ppo_model_latest.zip"
    print(f"Loading model from {MODEL_PATH}...")
    model = PPO.load(MODEL_PATH)
    
    obs, info = env.reset()
    print("--- STARTING TEST RUN ---")
    print("Press Ctrl+C to stop.")    

    try:
        while True:
            # deterministic=True is CRITICAL here! 
            # It tells the AI to use its best learned moves, with ZERO random guessing.
            action, _states = model.predict(obs, deterministic=True)
            
            # Take a step in the environment
            obs, reward, terminated, truncated, info = env.step(action)
            
            # If the spider falls or hits the 500 step limit, reset it
            if terminated or truncated:
                print("Episode finished. Resetting...")
                obs, info = env.reset()
                
    except KeyboardInterrupt:
        print("\n--- TEST STOPPED BY USER ---")
    finally:
        env.close()

if __name__ == '__main__':
    test()