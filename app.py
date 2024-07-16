from flask import Flask, render_template, request, jsonify
import requests
import schedule
import threading
import time

app = Flask(__name__)

class WebRobot:
    def __init__(self):
        self.url = None
        self.running = False

    def access_page(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                print(f"Accessed {self.url} successfully.")
            else:
                print(f"Failed to access {self.url}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def start(self, url):
        self.url = url
        self.running = True
        schedule.every(2).minutes.do(self.access_page)
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.running = False
        schedule.clear()

robot = WebRobot()
robot_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_robot():
    global robot_thread
    url = request.json.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'URL is required'})
    
    robot_thread = threading.Thread(target=robot.start, args=(url,))
    robot_thread.start()
    return jsonify({'status': 'success', 'message': 'Robot started'})

@app.route('/stop', methods=['POST'])
def stop_robot():
    global robot_thread
    robot.stop()
    robot_thread.join()
    return jsonify({'status': 'success', 'message': 'Robot stopped'})

if __name__ == '__main__':
    app.run(debug=True)
