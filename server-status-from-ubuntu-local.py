import time
import subprocess
import ping3
import redis
import math

# Function to ping the server
def ping_server(server_address, count=1, timeout=15):
    try:
        ping = ping3.ping(server_address, count, timeout)
        if ping is not None:
            return True  # Server is reachable
        else:
            return False  # Server is not reachable
    except Exception as e:
        print(f"Error during ping: {e}")
        return False  # An error occurred during ping

# Function to save status in Redis cache
def save_status_to_redis(server_address, status):
    try:
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        redis_key = f"server_status:{server_address}"
        redis_client.set(redis_key, int(status))
        redis_client.expire(redis_key, 60)  # Set expiration time (e.g., 60 seconds)
        print(f"Status saved to Redis: Server {server_address} is {'up' if status else 'down'}")
    except Exception as e:
        print(f"Error during Redis save: {e}")

# Function to send desktop notification using notify-send
def send_notification(server_name, down_duration):
    minutes = math.ceil(down_duration/60) # Calculate since from howmuch minutes server was down.
    notification_command = [
        "notify-send",
        "-i",
        "error",
        f"{server_name}",
        f"Server down since the last {minutes} minutes."
        "Please take a prompt look and resolve the server down issue as soon as possible.",
    ]
    subprocess.run(notification_command)

# Main function
def main():
    server_address = "8.8.8.8"  # Replace with the server you want to ping
    server_name = "Google Server"  # Replace with the name of your server
    down_duration_threshold = 600  # Replace with the 10 minutes (in seconds)

    down_duration = 0

    while True:
        status = ping_server(server_address)
        save_status_to_redis(server_address, status)
        if not status:
            down_duration += 60  # Add 60 seconds to down duration
        else:
            down_duration = 0  # Reset down duration if the server is up

        if down_duration >= down_duration_threshold:
            send_notification(server_name, down_duration)
            down_duration = 0  # Reset down duration after sending notification

        time.sleep(60)  # Ping every 60 seconds (adjust as needed)

if __name__ == "__main__":
    main()
