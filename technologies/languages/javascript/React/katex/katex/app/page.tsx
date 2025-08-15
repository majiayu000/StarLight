'use client';
import Image from "next/image";
import MathComponent from "./components/katex/Render";
import { useState } from "react";
import ExamplePage from "./components/katex/ReactKatex";
import AutoRender from "./components/katex/AutoRender";
export default function Home() {

  const str1 = "\\frac{n!}{k!(n-k)!} = \\binom{n}{k}";
  const [input, setInput] = useState("");
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <input type="text" value={input} onChange={(e) => setInput(e.target.value)} />
      <MathComponent formula={input} />

      {/* <ExamplePage /> */}
      <AutoRender />

    </main>
  );
}
