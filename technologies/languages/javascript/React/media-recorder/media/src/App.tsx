
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

import "./App.css";
import { useState, useRef } from "react";
import AudioRecorder from './components/audio/AudioRecoder';
import VideoRecorder from './components/audio/VideoRecorder';

const App = () => {
  let [recordOption, setRecordOption] = useState("video");
  const toggleRecordOption = (type) => {
    return () => {
      setRecordOption(type);
    };
  };
  return (
    <div>
      <h1>React Media Recorder</h1>
      <div className="button-flex">
        <button onClick={toggleRecordOption("video")}>
          Record Video
        </button>
        <button onClick={toggleRecordOption("audio")}>
          Record Audio
        </button>
      </div>
      <div>
        {recordOption === "video" ? <VideoRecorder /> : <AudioRecorder />}
      </div>
    </div>
  );
};
export default App;