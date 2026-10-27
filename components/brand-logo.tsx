export function BrandLogo({compact=false,className=""}:{compact?:boolean;className?:string}){
 // Brand mark displayed inside a fixed-size container (object-contain).
 // A plain <img> is intentional here: the logo is a decorative raster asset
 // whose container size varies per call site, so next/image fill-mode would
 // add complexity without benefit.
 return <span className={`inline-flex shrink-0 items-center justify-center ${className}`}>
   {/* eslint-disable-next-line @next/next/no-img-element */}
   <img src={compact?"/sellers-trust-network-mark.png":"/sellers-trust-network-logo.png"} alt={compact?"Sellers Trust Network mark":"Sellers Trust Network"} className="h-full w-full object-contain"/>
 </span>;
}
