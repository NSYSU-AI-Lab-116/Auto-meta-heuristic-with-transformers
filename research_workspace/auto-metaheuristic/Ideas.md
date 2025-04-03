# 一些想法都可以放這裡

- 對於被Discard的 meta-heuristic-like hyper-param optimizer, 有個想法是可以在每個隱藏層中間放置mutual layer(通用層)(可以是全連接層), 用來對模型內部 layer 做調整(移除、新增、更換參數等等), mutual layer 可以提供直接抽取模型中間層的機會, 使架構中的 retrain 的 cost 更小
