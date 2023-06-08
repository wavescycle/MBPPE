import ndarray from "ndarray";
import unpack from "ndarray-unpack";

export default function (arrayBufferContents) {
  // const version = arrayBufferContents.slice(6, 8); // Uint8-encoded
  const dtypes = {
    "<u1": {
      name: "uint8",
      size: 8,
      arrayConstructor: Uint8Array,
    },
    "|u1": {
      name: "uint8",
      size: 8,
      arrayConstructor: Uint8Array,
    },
    "<u2": {
      name: "uint16",
      size: 16,
      arrayConstructor: Uint16Array,
    },
    "|i1": {
      name: "int8",
      size: 8,
      arrayConstructor: Int8Array,
    },
    "<i2": {
      name: "int16",
      size: 16,
      arrayConstructor: Int16Array,
    },
    "<u4": {
      name: "uint32",
      size: 32,
      arrayConstructor: Int32Array,
    },
    "<i4": {
      name: "int32",
      size: 32,
      arrayConstructor: Int32Array,
    },
    "<u8": {
      name: "uint64",
      size: 64,
      arrayConstructor: BigUint64Array,
    },
    "<i8": {
      name: "int64",
      size: 64,
      arrayConstructor: BigInt64Array,
    },
    "<f4": {
      name: "float32",
      size: 32,
      arrayConstructor: Float32Array,
    },
    "<f8": {
      name: "float64",
      size: 64,
      arrayConstructor: Float64Array,
    },
  };
  const headerLength = new DataView(arrayBufferContents.slice(8, 10)).getUint8(
    0
  );
  const offsetBytes = 10 + headerLength;

  let hcontents = new TextDecoder("utf-8").decode(
    new Uint8Array(arrayBufferContents.slice(10, 10 + headerLength))
  );
  let header = JSON.parse(
    hcontents
      .toLowerCase() // True -> true
      .replace(/'/g, '"')
      .replace("(", "[")
      .replace(/,*\),*/g, "]")
  );
  let shape = header.shape;

  let dtype = dtypes[header.descr];
  let nums = new dtype["arrayConstructor"](arrayBufferContents, offsetBytes);

  return {
    data: unpack(ndarray(nums, shape)),
    shape,
  };
}

