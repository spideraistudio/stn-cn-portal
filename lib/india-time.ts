const timeZone="Asia/Kolkata";
export function formatIndiaDateTime(value:string|number|Date){const date=normalise(value);return new Intl.DateTimeFormat("en-IN",{timeZone,dateStyle:"medium",timeStyle:"short",hour12:true}).format(date)+" IST";}
export function formatIndiaDate(value:string|number|Date){return new Intl.DateTimeFormat("en-IN",{timeZone,dateStyle:"medium"}).format(normalise(value));}
function normalise(value:string|number|Date){if(typeof value==="number"&&value<100000000000)return new Date(value*1000);return value instanceof Date?value:new Date(value);}
