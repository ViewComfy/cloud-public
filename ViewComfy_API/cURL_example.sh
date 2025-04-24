# Example of how to call the ViewComfy API using cURL
# Replace the variables with your own values
curl -X POST "<ViewComfy_API_URL>" \
  -H "client_id: <Client_ID>" \
  -H "client_secret: <Client_Secret>" \
  -F "logs=false" \
  -F 'params={"50-inputs-text": "blurry, worst, bad quality, bad anatomy, embedding:-bad-artist-anime, distort, disfigure, low res, warp, deform, big eyes"}' \
  -F "47-inputs-image=@<Image_Path>" \
  --max-time 2400 \
  -L
