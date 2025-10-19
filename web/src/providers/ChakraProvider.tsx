"use client";

import { ChakraProvider } from "@chakra-ui/react";
import { ReactNode } from "react";

interface Props { children: ReactNode; }

export default function AppProviders({ children }: Props) {
  return <ChakraProvider>{children}</ChakraProvider>;
}
