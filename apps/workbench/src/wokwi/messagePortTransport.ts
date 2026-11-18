// Adapted from wokwi/wokwi-embed-example (MIT © CodeMagic LTD)

export class MessagePortTransport {
  onMessage: (message: unknown) => void = () => undefined;

  constructor(private readonly port: MessagePort) {
    this.port.onmessage = (event) => {
      this.onMessage(event.data);
    };
    this.port.start();
  }

  send(message: unknown) {
    this.port.postMessage(message);
  }
}
