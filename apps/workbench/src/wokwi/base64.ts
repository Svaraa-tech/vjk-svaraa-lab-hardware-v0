// Adapted from wokwi/wokwi-embed-example (MIT © CodeMagic LTD)

const B64 =
  "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

export function byteArrayToBase64(buf: Uint8Array): string {
  let result = "";
  for (let i = 0; i < buf.length - 2; i += 3) {
    result += B64[buf[i] >> 2];
    result += B64[((buf[i] & 0x03) << 4) | (buf[i + 1] >> 4)];
    result += B64[((buf[i + 1] & 0x0f) << 2) | (buf[i + 2] >> 6)];
    result += B64[buf[i + 2] & 0x3f];
  }
  if (buf.length % 3 === 1) {
    result += B64[buf[buf.length - 1] >> 2];
    result += B64[(buf[buf.length - 1] & 0x03) << 4];
    result += "==";
  }
  if (buf.length % 3 === 2) {
    result += B64[buf[buf.length - 2] >> 2];
    result +=
      B64[((buf[buf.length - 2] & 0x03) << 4) | (buf[buf.length - 1] >> 4)];
    result += B64[(buf[buf.length - 1] & 0x0f) << 2];
    result += "=";
  }
  return result;
}
