from flask import Flask, request, jsonify, send_from_directory
import copy
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend/srtf-frontend/build', static_url_path='/')
CORS(app)

def srtf_scheduling(processes):
    n = len(processes)
    # Deep copy to avoid modifying input
    proc = copy.deepcopy(processes)
    # Track remaining burst time
    remaining_time = [p["burst_time"] for p in proc]
    complete = 0
    time = 0
    min_remaining = float('inf')
    shortest = -1
    check = False
    gantt = []

    # Run until all processes are completed
    while complete != n:
        # Find process with minimum remaining time at current time
        for j in range(n):
            if (proc[j]["arrival_time"] <= time and 
                remaining_time[j] < min_remaining and 
                remaining_time[j] > 0):
                min_remaining = remaining_time[j]
                shortest = j
                check = True

        if not check:
            time += 1
            gantt.append({"process": "Idle", "start": time - 1, "end": time})
            continue

        # Execute the shortest process for 1 unit of time
        remaining_time[shortest] -= 1
        min_remaining = remaining_time[shortest]
        gantt.append({"process": proc[shortest]["name"], "start": time, "end": time + 1})
        time += 1

        # If process is complete
        if remaining_time[shortest] == 0:
            complete += 1
            check = False
            min_remaining = float('inf')
            proc[shortest]["finish_time"] = time
            proc[shortest]["turnaround_time"] = proc[shortest]["finish_time"] - proc[shortest]["arrival_time"]
            proc[shortest]["waiting_time"] = proc[shortest]["turnaround_time"] - proc[shortest]["burst_time"]

    # Calculate averages
    avg_waiting = sum(p["waiting_time"] for p in proc) / n
    avg_turnaround = sum(p["turnaround_time"] for p in proc) / n

    return {"processes": proc, "gantt": gantt, "avg_waiting": avg_waiting, "avg_turnaround": avg_turnaround}

@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.get_json()
    processes = data.get("processes", [])
    if not processes:
        return jsonify({"error": "No processes provided"}), 400

    result = srtf_scheduling(processes)
    return jsonify(result)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Use environment variable PORT, default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)