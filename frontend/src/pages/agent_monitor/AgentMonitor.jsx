import { useState } from "react";

export default function AgentMonitor() {

  const [logs, setLogs] = useState([]);

  const startSocket = () => {

    const socket = new WebSocket(
      "ws://127.0.0.1:8000/ws"
    );

    socket.onopen = () => {

      socket.send(
        "Explain transformer architecture"
      );

    };

    socket.onmessage = (event) => {

      setLogs(
        prev => [
          ...prev,
          event.data
        ]
      );

    };

  };

  return (

    <div>

      <button onClick={startSocket}>
        Start Agents
      </button>

      {
        logs.map(
          (log, index) => (

            <p key={index}>
              {log}
            </p>

          )
        )
      }

    </div>

  );

}