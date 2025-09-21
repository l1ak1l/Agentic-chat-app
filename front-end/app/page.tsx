'use client';

import { useState, useEffect } from 'react';
import { AtSign, ChevronDown, CornerDownLeft, Search } from 'lucide-react';

export default function Home() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [currentSampleIndex, setCurrentSampleIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);

  const samplePrompts = [
    "How do I create a dashboard for monitoring CPU usage?",
    "What's the best way to set up alerting rules?",
    "Help me troubleshoot high memory usage alerts"
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setIsLoading(true);
      // Simulate API call
      setTimeout(() => setIsLoading(false), 3000);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  // Dynamic typing animation for sample prompts
  useEffect(() => {
    const currentPrompt = samplePrompts[currentSampleIndex];
    let timeoutId: NodeJS.Timeout;

    if (isTyping) {
      if (displayedText.length < currentPrompt.length) {
        timeoutId = setTimeout(() => {
          setDisplayedText(currentPrompt.slice(0, displayedText.length + 1));
        }, 50);
      } else {
        timeoutId = setTimeout(() => {
          setIsTyping(false);
        }, 2000);
      }
    } else {
      if (displayedText.length > 0) {
        timeoutId = setTimeout(() => {
          setDisplayedText(displayedText.slice(0, -1));
        }, 30);
      } else {
        setCurrentSampleIndex((prev) => (prev + 1) % samplePrompts.length);
        setIsTyping(true);
      }
    }

    return () => clearTimeout(timeoutId);
  }, [displayedText, isTyping, currentSampleIndex, samplePrompts]);

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4 overflow-hidden relative">
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-black via-gray-900/20 to-black"></div>
      
      {/* Animated background dots */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-pink-500 rounded-full animate-pulse"></div>
        <div className="absolute top-3/4 left-3/4 w-1 h-1 bg-purple-400 rounded-full animate-ping" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 right-1/4 w-1.5 h-1.5 bg-orange-400 rounded-full animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>
      
      <div className="relative z-10 max-w-4xl mx-auto text-center space-y-8">
        {/* Badge */}
        {/* <div className="inline-flex items-center px-4 py-2 rounded-full bg-yellow-400 text-black text-sm font-semibold tracking-wide">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
          PUBLIC PREVIEW v0.1.15
        </div> */}
        
        {/* Main Heading */}
        <div className="space-y-4">
          <h1 className="text-5xl md:text-7xl font-bold text-white leading-tight">
            Hi, I'm{' '}
            <span className="bg-gradient-to-r from-pink-500 via-purple-500 to-pink-500 bg-clip-text text-transparent animate-pulse">
              Carbonflux Assistant
            </span>
          </h1>
          
          {/* Subheading */}
          <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
            A purpose-built{' '}
            <span className="bg-gradient-to-r from-pink-400 via-orange-400 to-purple-400 bg-clip-text text-transparent font-semibold">
              agentic LLM assistant
            </span>
            {' '}for Grafana that helps you learn, investigate, make changes and more.
          </p>
        </div>
        
        {/* Search Input */}
        <div className="max-w-4xl mx-auto mt-12">
          <form onSubmit={handleSubmit} className="relative">
            {/* Glowing border container */}
            <div className={`relative rounded-2xl p-[2px] ${isLoading ? 'animate-pulse-fast' : ''}`}>
              {/* Animated gradient border */}
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r from-pink-500 via-orange-400 via-purple-500 via-pink-500 to-orange-400 ${isLoading ? 'animate-gradient-fast' : 'animate-gradient'}`}></div>
              
              {/* Input container */}
              <div className="relative bg-gray-900/95 backdrop-blur-sm rounded-2xl">
                {/* External glow effect */}
                <div className="absolute -inset-4 rounded-2xl bg-gradient-to-r from-pink-500/30 via-orange-400/30 to-purple-500/30 blur-2xl opacity-75"></div>
                
                {/* Input field */}
                <div className="relative flex items-center p-6">
                  {/* @ Icon */}
                  <AtSign className="text-gray-400 mr-6 flex-shrink-0" size={28} />
                  
                  {/* Input */}
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Add context to improve results"
                    className="flex-1 bg-transparent text-white text-xl placeholder-gray-400 focus:outline-none py-2"
                    disabled={isLoading}
                  />
                  
                  {/* Right side icons */}
                  <div className="flex items-center space-x-4 ml-6">
                    <ChevronDown className="text-gray-400 hover:text-white transition-colors cursor-pointer" size={24} />
                    
                    {/* Web Search Toggle */}
                    <button
                      type="button"
                      onClick={() => setWebSearchEnabled(!webSearchEnabled)}
                      className={`flex items-center justify-center w-10 h-10 rounded-lg transition-all duration-200 ${
                        webSearchEnabled 
                          ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white' 
                          : 'bg-gray-700 text-gray-400 hover:bg-gray-600 hover:text-white'
                      }`}
                    >
                      <Search size={18} />
                    </button>
                    
                    <button
                      type="submit"
                      disabled={!query.trim() || isLoading}
                      className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <CornerDownLeft className="text-white" size={18} />
                    </button>
                  </div>
                </div>
                
                {/* Sample prompts with typing animation - inside input container */}
                {!query && (
                  <div className="px-6 pb-4 -mt-2">
                    <div className="h-6 flex items-center">
                      <span className="text-gray-500 text-sm italic">
                        "{displayedText}"
                        <span className="animate-pulse">|</span>
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2">
                <div className="flex items-center space-x-2 text-gray-400 text-sm">
                  <div className="animate-spin w-4 h-4 border-2 border-pink-400 border-t-transparent rounded-full"></div>
                  <span>Processing your query...</span>
                </div>
              </div>
            )}
          </form>
        </div>
        
        {/* Subtle hint text */}
        <p className="text-gray-500 text-sm mt-12">
          Press <kbd className="px-2 py-1 bg-gray-800 rounded text-xs">Enter</kbd> to send or use the dropdown for quick actions
        </p>
      </div>
    </div>
  );
}