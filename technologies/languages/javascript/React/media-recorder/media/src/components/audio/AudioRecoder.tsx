import { useState, useRef } from "react";
import "./index.css"


const mimeType = "audio/webm";


const AudioRecorder = () => {
  const [permission, setPermission] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);

  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const [recordingStatus, setRecordingStatus] = useState("inactive");
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [audio, setAudio] = useState<string | null>(null);

  const getMicrophonePermission = async () => {
    console.log("start get permission")
    if ("MediaRecorder" in window) {
      try {
        const streamData = await navigator.mediaDevices.getUserMedia({
          audio: true,
          video: false,
        });

        setPermission(true);
        setStream(streamData);
      } catch (err: any) {
        if (err instanceof Error) {
          console.error("捕获到错误:", err.message);
        } else {
          console.error("捕获到错误，但是类型不是 Error:", err);
        }
      }
    } else {
      alert("The MediaRecorder API is not supported in your browser.")

    }
  };

  const startRecording = async () => {
    const streamData = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: false,
    });

    setPermission(true);
    setStream(streamData);
    setRecordingStatus("recording");

    console.log("start")


    //create new Media recorder instance using the stream
    if (stream) {
      console.log("start has stream")
      const media = new MediaRecorder(stream);
      //set the MediaRecorder instance to the mediaRecorder ref
      mediaRecorder.current = media;
      //invokes the start method to start the recording process
      mediaRecorder.current.start();
      let localAudioChunks: Blob[] = [];
      mediaRecorder.current.ondataavailable = (event) => {
        if (typeof event.data === "undefined") return;
        if (event.data.size === 0) return;
        localAudioChunks.push(event.data);
      };
      setAudioChunks(localAudioChunks);

      // stream.getTracks().forEach(function (track) {
      //   console.log("stop!!")
      //   track.stop();
      // });
    }

  };

  const stopRecording = () => {
    setRecordingStatus("inactive");
    //stops the recording instance
    if (mediaRecorder.current) {
      mediaRecorder.current.stop();
      console.log("start stop")
      mediaRecorder.current.onstop = () => {
        console.log("on stop")
        //creates a blob file from the audiochunks data
        const audioBlob = new Blob(audioChunks, { type: mimeType });
        //creates a playable URL from the blob file.
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudio(audioUrl);
        setAudioChunks([]);
        if (stream) {
          stream.getTracks()[0].stop();
          setStream(null);
        }
        setPermission(false)

      }

    };
  };

  return (
    <div>
      <h2>Audio Recorder</h2>
      <main>
        <div className="audio-controls">
          {!permission ? (
            <button onClick={getMicrophonePermission} type="button">
              Get Microphone
            </button>
          ) : null}
          {recordingStatus === "inactive" ? (
            <button onClick={startRecording} type="button">
              Start Recording
            </button>
          ) : null}
          {recordingStatus === "recording" ? (
            <button onClick={stopRecording} type="button">
              Stop Recording
            </button>
          ) : null}

          {audio ? (
            <div className="audio-container">
              <audio src={audio} controls></audio>
              <a download href={audio}>
                Download Recording
              </a>
            </div>
          ) : null}
        </div>


      </main>
    </div>
  );
};

export default AudioRecorder;