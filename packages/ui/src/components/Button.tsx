import React from "react";
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {variant?:"primary"|"secondary"|"danger"|"ghost";size?:"sm"|"md"|"lg";loading?:boolean;children:React.ReactNode;}
export function Button({variant="primary",size="md",loading=false,disabled,children,className="",...props}:ButtonProps):React.ReactElement {
  const v={primary:"bg-indigo-600 text-white hover:bg-indigo-700",secondary:"bg-gray-100 text-gray-900 hover:bg-gray-200",danger:"bg-red-600 text-white hover:bg-red-700",ghost:"bg-transparent text-gray-700 hover:bg-gray-100"};
  const s={sm:"px-3 py-1.5 text-sm",md:"px-4 py-2 text-base",lg:"px-6 py-3 text-lg"};
  return <button {...props} disabled={disabled??loading} className={["inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed",v[variant],s[size],className].join(" ")}>{loading&&<span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"/>}{children}</button>;
}
