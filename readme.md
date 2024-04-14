## pip
書き出し：`pip freeze > requirements.txt`
読み込み：`pip install -r requirements.txt`

## run
`flask run --debug --reload`
ポート5000で走る

## リッチメニュー
### CR(U)D
Create
```sh
curl -v -X POST https://api.line.me/v2/bot/richmenu \
-H "Authorization: Bearer ${CHANNEL_ACCESS_TOKEN}" \
-H 'Content-Type: application/json' \
-d \
'{
    "size": {
      "width": 2500,
      "height": 843
    },
    "selected": false,
    "name": "Nice rich menu",
    "chatBarText": "Tap to open",
    "areas": [
      {
        "bounds": {
          "x": 0,
          "y": 0,
          "width": 2500,
          "height": 843
        },
        "action": {
          "type": "postback",
          "data": "action=buy&itemid=123"
        }
      }
   ]
}'
```
(Upload)
```sh
curl -v -X POST https://api-data.line.me/v2/bot/richmenu/${RICH_MENU_ID}/content \
-H "Authorization: Bearer ${CHANNEL_ACCESS_TOKEN}" \
-H "Content-Type: image/jpeg" \
-T image.jpg
```
Read(List)
```sh
curl -v -X GET https://api.line.me/v2/bot/richmenu/list \
-H "Authorization: Bearer ${CHANNEL_ACCESS_TOKEN}"
```
Read
```sh
curl -v -X GET https://api.line.me/v2/bot/richmenu/${RICH_MENU_ID} \
-H "Authorization: Bearer ${CHANNEL_ACCESS_TOKEN}"
```
Delete
```sh
curl -v -X DELETE https://api.line.me/v2/bot/richmenu/${RICH_MENU_ID} \
-H "Authorization: Bearer ${CHANNEL_ACCESS_TOKEN}"
```

### デフォルトリッチメニューの設定
設定
```sh
curl -v -X POST https://api.line.me/v2/bot/user/all/richmenu/${RICH_MENU_ID} \
-H "Authorization: Bearer ${CHANNEL_ACCESS_TOKEN}"
```
現デフォルトのID取得
```sh
curl -v -X GET https://api.line.me/v2/bot/user/all/richmenu \
-H "Authorization: Bearer ${CHANNEL_ACCESS_TOKEN}"
```
解除
```sh
curl -v -X DELETE https://api.line.me/v2/bot/user/all/richmenu \
-H "Authorization: Bearer ${CHANNEL_ACCESS_TOKEN}"
```
