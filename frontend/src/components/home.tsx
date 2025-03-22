'use client'

import { SplineScene } from "./ui/splite";
import { Card } from "./ui/card"
import { Spotlight } from "./ui/spotlight"
import { PulsatingButton } from "./ui/button"
import { useNavigate } from 'react-router-dom';  // ✅ Import navigation hook

 
export function SplineSceneBasic() {


  const navigate = useNavigate();  // ✅ Initialize navigation

  const handleNavigate = () => {
    navigate('/chat');  // ✅ Navigate to /chat page on button click

  }
  return (
    <Card className="w-full h-[535px] bg-black/[0.96] relative overflow-hidden">
      <Spotlight
        className="-top-40 left-0 md:left-60 md:-top-20"
        fill="white"
      />
      
      <div className="flex h-full">
        {/* Left content */}
        <div className="flex-1 p-8 relative z-10 flex flex-col justify-center">
          <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400">
            AI For Growth
          </h1>
          <p className="mt-4 text-m text-neutral-300 max-w-lg">
          "Information Chatbot – Powered by AI, Delivering Real-Time Insights with RAG Technology"
          </p>
          {/* Try Now Button */}
          <PulsatingButton
            onClick={handleNavigate}  // ✅ Navigate on click
            className="mt-10 ml-46 relative bg-white text-white font-bold py-2 w-32 py-2 rounded-lg 
            shadow-lg transition-transform transform hover:scale-120 
            before:absolute before:inset-0 before:rounded-lg 
            before:bg-white before:opacity-0 before:animate-pulse"
          >
            Try Now
          </PulsatingButton>
        </div>

        {/* Right content */}
        <div className="flex-1 relative">
          <SplineScene 
            scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
            className="w-full h-full"
          />
        </div>
      </div>
    </Card>
  )
}

