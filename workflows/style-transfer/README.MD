# Style Transfer ViewComfy API Call Example

### Install dependencies to run the project

```
npm install
```

### Run the project

Change the viewComfyUrl value to the ViewComfy endpoint from the app.viewcomfy.com
viewComfyUrl value is inside `style_transfer_api.ts` file

In the `style_transfer_call.ts` file, you can change the parameters of the workflow

and to make the API call run:

```
npm run dev
```

the result will be something like this:

### Inputs

<img src="https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/style-transfer/composition_image.jpg" alt="composition image" width=50% height=50%>
<img src="https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/style-transfer/style.png" alt="style" width=50% height=50%>

### Output

![style transfer result](https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/style-transfer/style_transfer_result.png "style transfer")
