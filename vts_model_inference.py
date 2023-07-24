import torch
import pyaudio
from vtube_studio.vts import VTS_API
import time
import asyncio
import keyboard
import numpy as np
from ai.vtubernet import VtuberNet

URL = "ws://localhost:8001/"
MIC_INPUT = "Enter Audio Input Here"

model = VtuberNet()
model.load_state_dict(torch.load("vtuber_model.pth"))
model.eval()

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

        sample_format = pyaudio.paFloat32
        channels = 1

        stream = pa.open(
            format=sample_format,
            channels=channels,
            rate=model.sample_rate,
            frames_per_buffer=model.segment,
            input_device_index=desired_device_index,
            input=True
        )
        stream.start_stream()

        params_config = await vtube_studio.get_parameters()

        start = 0
        while True:
            print(str(time.time()-start))
            while time.time() - start < .1:
                await asyncio.sleep(.001)
            start = time.time()
            data = stream.read(model.segment)

            audio_data = np.frombuffer(data, dtype=np.float32)
            test_data = torch.tensor(audio_data)

            with torch.no_grad():
                output = model(test_data)
                
            await vtube_studio.nn_movement(output.flatten().tolist(), params_config)

            if keyboard.is_pressed('del'):
                break

    stream.stop_stream()
    stream.close()
    pa.terminate()

if(__name__ == '__main__'):
    asyncio.run(main())