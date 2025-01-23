import uuid
import websocket
import json
import random
import asyncio
import requests


generation_parameters = {
    "input_path": "img.jpg",
    "positive_prompt": "a cat walking on a fence",
}

class ComfyUIService():
    def __init__(self, server_address='127.0.0.1:2222', workflow_path='workflow_api.json'):
        self.server_address = server_address
        self.workflow_path = workflow_path
       
    async def establish_connection(self):
        client_id = str(uuid.uuid4())
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.server_address}/ws?clientId={client_id}")
        return ws, self.server_address, client_id
    
    def load_workflow(self, workflow_path):
        with open(workflow_path, 'r') as file:
            return json.load(file)
        
    async def queue_prompt(self, prompt, client_id, server_address):
        """Queue a workflow for execution. The prompt here is the full workflow_api.json file"""
        data = {"prompt": prompt, "client_id": client_id}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"http://{server_address}/prompt", json=data, headers=headers)
        return response.json()
        
    def update_workflow(self, prompt, input_path, positive_prompt):
        id_to_class_type = {id: details['class_type'] for id, details in prompt.items()}
        k_sampler = [key for key, value in id_to_class_type.items() if value == 'KSampler'][0]

        """Set the seed to random"""
        prompt.get(k_sampler)['inputs']['seed'] = random.randint(10**14, 10**15 - 1)

        """Update the positive prompt"""
        text_prompt = prompt.get(k_sampler)['inputs']['positive'][0]
        prompt.get(text_prompt)['inputs']['text'] = positive_prompt

        """Update the path to the input image"""
        image_loader = [key for key, value in id_to_class_type.items() if value == 'LoadImage'][0]
        filename = input_path.split('/')[-1]
        prompt.get(image_loader)['inputs']['image'] = filename

        return prompt
    
    def track_progress(self, ws, prompt_id):
        """Track the progress of image generation"""
        while True:
            try:
                message = json.loads(ws.recv())
                if message['type'] == 'progress':
                    '''If the workflow is running print k-sampler current step over total steps'''
                    print(f"Progress: {message['data']['value']}/{message['data']['max']}")
                
                elif message['type'] == 'executing':
                    '''Print the node that is currently being executed'''
                    print(f"Executing node: {message['data']['node']}")
                
                elif message['type'] == 'execution_cached':
                    '''Print list of nodes that are cached'''
                    print(f"Cached execution: {message['data']}")
                
                '''Check for completion'''
                if (message['type'] == 'executed' and 
                    'prompt_id' in message['data'] and 
                    message['data']['prompt_id'] == prompt_id):
                    print("Generation completed")
                    return True
                
            except Exception as e:
                print(f"Error processing message: {e}")
                return False
    
    async def get_history(self, prompt_id, server_address):
        """Fetch the output data for a completed workflow, returns a JSON with generation parameters and results filenames and directories"""
        response = requests.get(f"http://{server_address}/history/{prompt_id}")
        return response.json()

    async def get_image(self, filename, subfolder, folder_type, server_address):
        """Fetch results. Note that "save image" nodes will save image in the ouptut folder and "preview image" nodes will save image in the temp folder"""
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        response = requests.get(f"http://{server_address}/view", params=params)
        return response.content

    def upload_image(self, input_path, filename, server_address, folder_type="input", image_type="image", overwrite=False):
        """Upload an image or a mask to the ComfyUI server. input_path is the path to the image/mask to upload and image_type is either image or mask"""
        
        with open(input_path, 'rb') as file:
            files = {
                'image': (filename, file, 'image/png')
            }
            data = {
                'type': folder_type,
                'overwrite': str(overwrite).lower()
            }
            url = f"http://{server_address}/upload/{image_type}"
            response = requests.post(url, files=files, data=data)
            return response.content
       
    async def generate_image(self, generation_parameters):
        ws, _, client_id = await self.establish_connection()
       
        try:
            """Update the workflow with the generation parameters"""
            workflow = self.load_workflow('workflow_api.json')
            workflow = self.update_workflow(workflow, 
                                            input_path=generation_parameters['input_path'],
                                            positive_prompt=generation_parameters['positive_prompt']
                                            )
            
            """Upload the input image to the server"""
            self.upload_image(input_path=generation_parameters['input_path'], filename='img.jpg', server_address=self.server_address)
            
            """Send the workflow to the server"""
            prompt_id = await self.queue_prompt(workflow, client_id, self.server_address)
            prompt_id = prompt_id['prompt_id']

            """Track the progress"""
            completed = self.track_progress(ws, prompt_id)
            if not completed:
                print("Generation failed or interrupted")
                return None

            """Fetch the output data"""    
            history = await self.get_history(prompt_id, self.server_address)
            outputs = history[prompt_id]['outputs']

            '''Get output images'''
            for node_id in outputs:
                node_output = outputs[node_id]
                images_output = []
                if 'images' in node_output:
                    for image in node_output['images']:
                        image_data = await self.get_image(image['filename'], image['subfolder'], image['type'], self.server_address)
                        images_output.append(image_data)
            return images_output
           
        finally:
            ws.close()

async def main():
    service = ComfyUIService()
    image_output = await service.generate_image(generation_parameters)
    with open('output.png', 'wb') as file:
        file.write(image_output[0])

if __name__ == "__main__":
    asyncio.run(main())
