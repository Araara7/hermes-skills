# WebSocket Protocol Capture — Real Session Data

Captured from actual gameplay attempts (v6/v7/v8 scripts, 31 May 2026).

## Matchmaking Flow (Confirmed Working)

```
→ 42["general_connection","0x32e9151f7450949f3d4890f856de4a372f43d113"]
→ 42["matchmaking:join","0x32e9151f7450949f3d4890f856de4a372f43d113"]
← 42["matchmaking:update",{"status":"matched","gameId":"game_1780244762449_iNfo1jFY2QQKjD27VDc36a","opponent":{"username":"odenxo","usernameDisplay":"OdenXo",...}}]
```

Match found in 1-5 seconds consistently. ELO 811 range matches fast.

## Game Connection (After Match)

```
→ 42["_connect","game_1780244762449_iNfo1jFY2QQKjD27VDc36a","0x32e9151f7450949f3d4890f856de4a372f43d113"]
→ 42["select_point","game_1780244762449_iNfo1jFY2QQKjD27VDc36a","0x32e9151f7450949f3d4890f856de4a372f43d113",null]
```

`select_point` with `null` is sent automatically by the page. It's harmless.

## SELECTING Phase UI Text

```
174ms
Exit
Spectator Link
https://www.pixiechess.xyz/game/game_1780244762449_iNfo1jFY2QQKjD27VDc36a
otama777
SELECTING
00:45
OdenXo
SELECTING
II
Click or Drag to substitute in a Pixie piece.
MIN 3 • M
```

## Searching UI (Before Match)

```
otama777
RATING 811
Searching...
RANGE 575
Searching for Opponent
Kindly be patient while we find you a worthy foe. The bell will sound when the lobby is ready to begin.
SEARCHING FOR 0:15
Abandon Queue
```

## Game Start Events (Expected After SELECTING)

```
← 42["boardReady",...]           # Board initialized
← 42["sync",{"fen":"..."}]       # FEN position
← 42["possibleMoves",{"moves":[...]}]  # Your turn — list of legal moves
```

## Game Move Events

```
← 42["move",{"move":"e2e4","san":"e4"}]  # Opponent move
→ (no outgoing move message — clicks on canvas board)
```

## Game Over Events

```
← 42["gameOver",...]
← 42["endGameAnimationComplete",...]
```

## Key Observations

1. `matchmaking:join` is sent repeatedly by the app (every ~10s) — this is normal, not a bug
2. `_connect` is sent for each game connection
3. `select_point` with null is auto-sent during SELECTING
4. No `ready` or `confirm` WS message was captured — game starts automatically after countdown
5. Moves are made by clicking on the canvas board, not via WS messages
6. Binary WS messages exist: `451-["update",{"_placeholder":true,"num":0}]` + binary blob
