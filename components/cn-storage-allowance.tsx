'use client';
import {useState} from 'react';

export function CNStorageAllowance({maximum,defaultValue,className}:{maximum?:number;defaultValue:number;className?:string}){
 const [value,setValue]=useState(String(defaultValue));
 const amount=Number(value);
 const invalid=value!==''&&(!Number.isSafeInteger(amount)||amount<1||(maximum!==undefined&&amount>maximum));
 return <label>CN storage allowance (MiB)
  <input className={className} type="number" name="quota" min="1" step="1" max={maximum} value={value} onChange={e=>setValue(e.target.value)} aria-invalid={invalid} required/>
  <small className="block mt-1">{maximum===undefined?'Platform superadmin controls storage grants.':`Granted maximum: ${maximum.toLocaleString()} MiB per staff user. Only the platform superadmin can increase this maximum.`} Each person’s CN work stays private. STN storage is separate.</small>
  {invalid&&<span role="alert" className="block text-rose-700">{maximum===undefined?'Enter a positive whole number of MiB.':`Enter a whole number from 1 to ${maximum.toLocaleString()} MiB. This allowance cannot be saved.`}</span>}
 </label>;
}
