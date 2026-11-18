// Adapted from wokwi/wokwi-embed-example (MIT © CodeMagic LTD)

import { byteArrayToBase64 } from "./base64";
import type { MessagePortTransport } from "./messagePortTransport";

type Pending = [(result: unknown) => void, (err: Error) => void];

type ApiResponse = {
  type: "response";
  id?: string;
  result?: unknown;
  error?: boolean;
};

type ApiEvent = {
  type: "event";
  event: string;
  payload?: unknown;
  nanos?: number;
  paused?: boolean;
};

type ApiHello = { type: "hello"; [k: string]: unknown };

type ApiMessage = ApiHello | ApiEvent | ApiResponse;

export class WokwiClient extends EventTarget {
  private lastId = 0;
  private pendingCommands = new Map<string, Pending>();

  constructor(private readonly transport: MessagePortTransport) {
    super();
    this.transport.onMessage = (message) => {
      this.processMessage(message as ApiMessage);
    };
  }

  async fileUpload(name: string, content: string | ArrayBuffer | Uint8Array) {
    if (typeof content === "string") {
      return this.sendCommand("file:upload", { name, text: content });
    }
    const bytes =
      content instanceof Uint8Array ? content : new Uint8Array(content);
    return this.sendCommand("file:upload", {
      name,
      binary: byteArrayToBase64(bytes),
    });
  }

  async simStart(params: { firmware: string; elf: string }) {
    return this.sendCommand("sim:start", params);
  }

  async simPause() {
    return this.sendCommand("sim:pause");
  }

  async simResume(pauseAfter?: number) {
    return this.sendCommand("sim:resume", { pauseAfter });
  }

  async simRestart(opts?: { pause?: boolean }) {
    return this.sendCommand("sim:restart", { pause: opts?.pause });
  }

  async simStatus() {
    return this.sendCommand("sim:status") as Promise<{
      running: boolean;
      nanos: number;
    }>;
  }

  async serialMonitorListen() {
    return this.sendCommand("serial-monitor:listen");
  }

  async serialMonitorWrite(bytes: number[] | Uint8Array) {
    return this.sendCommand("serial-monitor:write", {
      bytes: Array.from(bytes),
    });
  }

  async gpioList() {
    return this.sendCommand("gpio:list") as Promise<{ pins: string[] }>;
  }

  async gpioWrite(pin: string, value: boolean) {
    return this.sendCommand("gpio:write", { pin, value });
  }

  async sendCommand(command: string, params?: unknown) {
    return new Promise((resolve, reject) => {
      const id = String(this.lastId++);
      this.pendingCommands.set(id, [resolve, reject]);
      this.transport.send({ type: "command", command, params, id });
    });
  }

  private processMessage(message: ApiMessage) {
    switch (message.type) {
      case "hello":
        this.dispatchEvent(
          new CustomEvent("wokwi:connected", { detail: message }),
        );
        break;
      case "event":
        this.dispatchEvent(
          new CustomEvent(message.event, { detail: message.payload }),
        );
        break;
      case "response": {
        const id = message.id ?? "";
        const pending = this.pendingCommands.get(id);
        if (!pending) {
          console.error("Unknown Wokwi response", message);
          return;
        }
        this.pendingCommands.delete(id);
        const [resolve, reject] = pending;
        if (message.error) {
          const result = message.result as
            | { code?: number; message?: string }
            | undefined;
          reject(
            new Error(
              `Error ${result?.code ?? "?"}: ${result?.message ?? "unknown"}`,
            ),
          );
        } else {
          resolve(message.result);
        }
        break;
      }
    }
  }
}
