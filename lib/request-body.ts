export class RequestBodyError extends Error {
  constructor(message:string, public status=413) { super(message); }
}

async function boundedBody(request:Request, maxBytes:number) {
  const declared = Number(request.headers.get("content-length") || 0);
  if (declared > maxBytes) throw new RequestBodyError("Request is too large.");
  const reader = request.body?.getReader();
  if (!reader) return new Uint8Array();
  const chunks:Uint8Array[]=[];
  let size=0;
  try {
    for (;;) {
      const {done,value}=await reader.read();
      if (done) break;
      size+=value.byteLength;
      if (size>maxBytes) { await reader.cancel(); throw new RequestBodyError("Request is too large."); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const bytes=new Uint8Array(size);let offset=0;
  for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
  return bytes;
}
export async function readJsonBody(request:Request) {
  const data=JSON.parse(new TextDecoder().decode(await boundedBody(request,32*1024)));
  if (!data || typeof data!=="object" || Array.isArray(data)) throw new RequestBodyError("Invalid request.",400);
  return data as Record<string,unknown>;
}
export async function readFormBody(request:Request) {
  const bytes=await boundedBody(request,6*1024*1024);
  return new Response(bytes,{headers:{"Content-Type":request.headers.get("content-type")||""}}).formData();
}
