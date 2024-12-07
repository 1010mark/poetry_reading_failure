import argparse
from pythonosc import dispatcher
from pythonosc import osc_server

def parse_osc_message(message):
    parsed = {}
    for i in range(0, len(message), 2):  # 2個ずつ取り出す
        key = message[i]
        value = message[i + 1]
        parsed[key] = value
    return parsed

def handle_cycles(address, *args):
    # ('_id_', '1', 'cps', 0.5625, 'cycle', 1311.4375, 'delta', 0.11111100018024445, 'orbit', 0, 's', 'sd')
    
    # message = parse_osc_message(args)  # TidalCyclesから送られてきた現在のcycles
   #  cycles = message["cycle"];
   # print(cycles)
    print(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=2020, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/*", handle_cycles)

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()