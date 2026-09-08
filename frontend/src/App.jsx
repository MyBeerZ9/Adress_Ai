import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';
import {
  Sparkles,
  MapPin,
  CheckCircle2,
  AlertCircle,
  Layers,
  Cpu,
  Globe,
  Compass,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

import Background3D from './components/Background3D';
import Navbar from './components/Navbar';
import AddressInput from './components/AddressInput';
import ParsedCard from './components/ParsedCard';
import MapView from './components/MapView';
import JsonViewer from './components/JsonViewer';
import Toast from './components/Toast';
import { parseAddress, checkBackendHealth } from './services/api';

export default function App() {
  const [address, setAddress] = useState(
    '2nd floor, pink building, near ICICI bank, Rajouri Garden, Delhi 110027'
  );
  const [isLoading, setIsLoading] = useState(false);
  const [parsedResult, setParsedResult] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [toast, setToast] = useState(null);
  const [isCopiedJson, setIsCopiedJson] = useState(false);
  const [isCopiedFormatted, setIsCopiedFormatted] = useState(false);

  // Check backend health periodically
  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      const online = await checkBackendHealth();
      if (isMounted) setBackendOnline(online);
    };

    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Trigger confetti burst on high-confidence parse
  const triggerConfetti = () => {
    try {
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.8 },
        colors: ['#a855f7', '#ec4899', '#06b6d4', '#ffffff'],
      });
    } catch {
      // Ignore if confetti fails in some environments
    }
  };

  const handleParse = async () => {
    if (!address.trim()) {
      showToast('Please provide an address to parse.', 'error');
      return;
    }

    setIsLoading(true);
    try {
      const result = await parseAddress(address);
      setParsedResult(result);
      showToast('Address parsed and geocoded successfully!', 'success');
      triggerConfetti();
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to parse address. Is backend running?', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setIsCopiedJson(true);
    showToast('JSON response copied to clipboard!', 'success');
    setTimeout(() => setIsCopiedJson(false), 2500);
  };

  const handleCopyFormatted = () => {
    if (parsedResult?.formatted_address) {
      navigator.clipboard.writeText(parsedResult.formatted_address);
      setIsCopiedFormatted(true);
      showToast('Formatted address copied!', 'success');
      setTimeout(() => setIsCopiedFormatted(false), 2500);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col text-white selection:bg-purple-500/30 selection:text-purple-200">
      {/* 3D Background */}
      <Background3D />

      {/* Navigation Header */}
      <Navbar backendOnline={backendOnline} />

      {/* Main Container */}
      <main className="relative z-10 flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-10 sm:space-y-14">
        {/* Hero Section */}
        <section className="text-center space-y-4 max-w-3xl mx-auto pt-2 sm:pt-6">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs sm:text-sm font-medium shadow-glow-sm"
          >
            <Sparkles className="w-4 h-4 text-pink-400" />
            <span>AI-Powered Indian Address Segmentation & Map Visualizer</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight"
          >
            Transform Messy Addresses into{' '}
            <span className="gradient-text">Precise Coordinates</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-base sm:text-lg text-white/60 leading-relaxed max-w-2xl mx-auto"
          >
            Segment Indian addresses with floor numbers, landmark cues, sublocalities, and 6-digit PIN codes into standardized structures with real-time geospatial rendering.
          </motion.p>
        </section>

        {/* Search & Parse Input Area */}
        <section>
          <AddressInput
            address={address}
            setAddress={setAddress}
            onParse={handleParse}
            isLoading={isLoading}
          />
        </section>

        {/* Results Section */}
        <AnimatePresence>
          {parsedResult && (
            <motion.section
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.6 }}
              className="space-y-8"
            >
              {/* Structured Breakdown + Interactive Map Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Left: Structured Components Breakdown (7 cols) */}
                <div className="lg:col-span-7 space-y-6">
                  <ParsedCard
                    result={parsedResult}
                    onCopyFormatted={handleCopyFormatted}
                    isCopied={isCopiedFormatted}
                  />
                </div>

                {/* Right: Leaflet Map View (5 cols) */}
                <div className="lg:col-span-5 space-y-6">
                  <MapView
                    coordinates={parsedResult.coordinates}
                    address={parsedResult.formatted_address}
                    components={parsedResult.structured_components}
                  />
                </div>
              </div>

              {/* Raw JSON & cURL Inspector */}
              <div className="pt-2">
                <JsonViewer
                  data={parsedResult}
                  onCopy={handleCopy}
                  isCopied={isCopiedJson}
                />
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        {/* Feature Highlights Grid */}
        <section className="pt-8 border-t border-white/10">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="glass-card glass-card-hover p-6 rounded-2xl border border-white/10 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                <Compass className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-bold text-white">Landmark-Aware Parsing</h4>
              <p className="text-sm text-white/60 leading-relaxed">
                Extracts "near ICICI bank", "behind hotel", and "opp mall" cues, using them to boost pinpoint geocoding accuracy.
              </p>
            </div>

            <div className="glass-card glass-card-hover p-6 rounded-2xl border border-white/10 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400">
                <Cpu className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-bold text-white">Confidence Scoring</h4>
              <p className="text-sm text-white/60 leading-relaxed">
                Dynamic 0–100% confidence meter computed from component coverage, postal circle matching, and geocode resolution.
              </p>
            </div>

            <div className="glass-card glass-card-hover p-6 rounded-2xl border border-white/10 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                <Globe className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-bold text-white">Multi-Engine Geocoding</h4>
              <p className="text-sm text-white/60 leading-relaxed">
                Supports Google Geocoding API with intelligent fallback to OpenStreetMap Nominatim and Indian metro databases.
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 bg-[#0f0c29]/80 backdrop-blur-xl py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-white/50">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-white">AddressAI</span>
            <span>•</span>
            <span>Production-Ready Indian Address Intelligence</span>
          </div>
          <div className="flex items-center gap-4">
            <span>FastAPI</span>
            <span>•</span>
            <span>React + Vite</span>
            <span>•</span>
            <span>Leaflet</span>
            <span>•</span>
            <span>Three.js</span>
            <span>•</span>
            <span>Tailwind CSS</span>
          </div>
        </div>
      </footer>

      {/* Global Toast */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
