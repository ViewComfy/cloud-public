import asyncio
import base64
from api import infer, infer_with_logs


async def api_examples():
    view_comfy_api_url = ""

    client_id = ""
    client_secret = ""

    # Set parameters
    params = {}
    params["625-inputs-image"] = open("pose_sheet.png", "rb")
    params["626-inputs-image"] = open("character.png", "rb")

    characterPrompt = "a attractive woman, dark long hair, a women wearing a grey wool turtleneck sweater, brown eyes, jeans, brown boots, short medium long hair, chin long hair that looks like she just got up, She has a fair complexion, expressive brown eyes, Her makeup is natural, highlighting her soft features. she has slightly pink cheeks and a healthy skin tone"

    params["594-inputs-string"] = characterPrompt

    params.update(
        {
            "82-inputs-upscale_by": 2,
            "426-inputs-string": "a deep forest with oaks and pine trees ferns and bushes, national park, close up, overcast, close up, amateur photography, shot on iphone, candid photo",
            "436-inputs-string": "a modern city during sunset, the sky is adorned by epic cloud formations, frontal close up, walking through the city, hard sunlight on face, Side lit, candid photography, dslr, evening, silhouette, moody, autumn, warm orange atmosphere, natural smile, amateur photography, shot on iphone, candid photo,  winking with one eye closed",
            "443-inputs-string": "music video, color gel lighting, dark background, fog, colorful lighting, looking away from camera, stage lighting, concert stage, neon colors, silhouette, darkness, moody, amateur photography, shot on iphone, candid photo",
            "458-inputs-string": "a vast desert landscape with distant mountains, the hard sunlight is illuminating the person from the side and casting shadows on to the white sand, blue sky, shadows, waving, close up, candid photography, shocked expression, side lit face, shocked expression with an open mouth, surprised face, amateur photography, shot on iphone, candid photo",
            "499-inputs-noise_seed": 384340151733840,
            "594-inputs-string": "a attractive woman, dark long hair, a women wearing a grey wool turtleneck sweater, brown eyes, jeans, brown boots, short medium long hair, chin long hair that looks like she just got up, She has a fair complexion, expressive brown eyes, Her makeup is natural, highlighting her soft features. she has slightly pink cheeks and a healthy skin tone",
            "608-inputs-string": "it is a masterpiece, amateur photography, shot on iphone",
        }
    )

    # Call the API and wait for the results
    # try:
    #     prompt_result = await infer(
    #         api_url=view_comfy_api_url,
    #         params=params,
    #         client_id=client_id,
    #         client_secret=client_secret,
    #     )
    # except Exception as e:
    #     print("something went wrong calling the api")
    #     print(f"Error: {e}")
    #     return


    def logging_callback(log_message: str):
        print(log_message)

    # Call the API and get the logs of the execution in real time
    # the console.log is the function that will be use to log the messages
    # you can use any function that you want
    try:
        prompt_result = await infer_with_logs(
            api_url=view_comfy_api_url,
            params=params,
            logging_callback=logging_callback,
            client_id=client_id,
            client_secret=client_secret,
        )
    except Exception as e:
        print("something went wrong calling the api")
        print(f"Error: {e}")
        return

    if not prompt_result:
        print("No prompt_result generated")
        return

    for file in prompt_result.outputs:
        try:
            # Decode the base64 data before writing to file
            binary_data = base64.b64decode(file.data)
            with open(file.filename, "wb") as f:
                f.write(binary_data)
            print(f"Successfully saved {file.filename}")
        except Exception as e:
            print(f"Error saving {file.filename}: {str(e)}")


if __name__ == "__main__":
    asyncio.run(api_examples())
