const osc = require("osc");

// 受信するポート (localhost:57120)
const udpPort = new osc.UDPPort({
    localAddress: "localhost",
    localPort: 57120,
});

// 転送先ポート (localhost:2020, 6010, 57121)
const sendPorts = [
    { address: "localhost", port: 2020 },
    { address: "localhost", port: 57121 }
];

// 受信したメッセージを転送する
udpPort.on("message", function (oscMessage) {
    try{
        console.log("Received OSC message: ", oscMessage);

        // 受信したメッセージを各転送先に送信
        sendPorts.forEach((sendPort) => {
            const udpClient = new osc.UDPPort({
                localAddress: "localhost",
                localPort: 0, // 自動的に空いているポートを選択
                remoteAddress: sendPort.address,
                remotePort: sendPort.port,
            });
    
            udpClient.open();
    
            // メッセージを送信
            udpClient.send(oscMessage);
        });
    }catch (e){
        console.error(e)
    }
});

// ポートを開いてメッセージをリッスン
udpPort.open();
console.log("Listening for OSC messages on localhost:57120");
