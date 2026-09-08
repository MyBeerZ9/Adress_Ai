import React from 'react';
import { Sparkles, MapPin, Layers, ExternalLink } from 'lucide-react';

export default function Navbar({ backendOnline }) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/10 bg-[#0f0c29]/70 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo & Brand */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl gradient-accent shadow-glow-sm">
            <MapPin className="w-5 h-5 text-white" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-pink-400 rounded-full border-2 border-[#0f0c29] animate-ping" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight text-white">
                Address<span className="gradient-text font-black">AI</span>
              </span>
              <span className="px-2 py-0.5 text-[10px] uppercase tracking-wider font-semibold rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-white/50 hidden sm:block">
              Intelligent Indian Address Parser & Geocoder
            </p>
          </div>
        </div>

        {/* Status Indicators & Links */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs text-white/80">
            <span
              className={`w-2 h-2 rounded-full ${
                backendOnline ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            />
            <span className="hidden md:inline">
              {backendOnline ? 'FastAPI Backend Online' : 'Connecting to API...'}
            </span>
            <span className="md:hidden">
              {backendOnline ? 'Online' : 'Connecting'}
            </span>
          </div>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-200 text-xs font-medium transition-all hover:scale-105"
          >
            <Layers className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Swagger Docs</span>
            <ExternalLink className="w-3 h-3 opacity-60" />
          </a>
        </div>
      </div>
    </header>
  );
}
