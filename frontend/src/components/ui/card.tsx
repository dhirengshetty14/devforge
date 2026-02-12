import { PropsWithChildren } from "react";
import { cn } from "@/lib/utils";

type CardProps = PropsWithChildren<{
  className?: string;
}>;

export function Card({ className, children }: CardProps) {
  return <div className={cn("glass rounded-2xl p-5 shadow-sm", className)}>{children}</div>;
}
