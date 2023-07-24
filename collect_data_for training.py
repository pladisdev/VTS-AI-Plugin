import pyaudio
from vtube_studio.vts import VTS_API
import asyncio 
import wave 
import keyboard
import time
from ai.vtubernet import DEFAULT_DURATION, DEFAULT_SAMPLE_RATE

URL = "ws://localhost:8001/"
MIC_INPUT = "Enter Audio Input Here"

async def main():
    async with VTS_API(URL) as vtube_studio:

        pa = pyaudio.PyAudio()

        desired_device_name = MIC_INPUT
        desired_device_index = None
        for i in range(pa.get_device_count()):
            device_info = pa.get_device_info_by_index(i)
            if desired_device_name in device_info["name"]:
                desired_device_index = i
                break

        duration = DEFAULT_DURATION
        sample_rate = DEFAULT_SAMPLE_RATE
        buffer_size = int(duration * sample_rate)
        sample_format = pyaudio.paFloat32
        channels = 1 

        stream = pa.open(
            format=sample_format,
            channels=channels,
            rate=sample_rate,
            frames_per_buffer=buffer_size,
            input_device_index=desired_device_index,
            input=True
        )
        stream.start_stream()

        bytes_buffer = bytes()
        params_buffer = []

        start = 0
        while True:
            print(str(time.time()-start))
            while time.time() - start < .1:
                await asyncio.sleep(.001)
            start = time.time()
            data = stream.read(buffer_size)
            bytes_buffer += data
            
            raw_params = await vtube_studio.get_parameters()
            params = []
            for param in raw_params:
                if param[0] in vtube_studio.model_params:
                    params.append(param[1])
            params_buffer.append(params)          

            if keyboard.is_pressed('del'):
                break

    stream.stop_stream()
    stream.close()

    with wave.open('training_data.wav', mode='wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(pa.get_sample_size(sample_format))
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes_buffer)

    pa.terminate()

    with open("training_data.txt", "a") as file:
        for params in params_buffer:
            file.write(", ".join(map(str, params)))
            file.write("\n")

if(__name__ == '__main__'):
    asyncio.run(main())