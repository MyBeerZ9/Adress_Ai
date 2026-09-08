import React from 'react';
import { motion } from 'framer-motion';
import { Search, Loader2, Sparkles, X, CornerDownLeft, MapPin } from 'lucide-react';

const SAMPLE_ADDRESSES = [
  {
    label: "Delhi (Landmark + Floor)",
    text: "2nd floor, pink building, near ICICI bank, Rajouri Garden, Delhi 110027",
  },
  {
    label: "Bengaluru (Apartment + Mall)",
    text: "Flat 402, Sai Residency, Opp. Forum Mall, Koramangala 7th Block, Bengaluru, Karnataka 560095",
  },
  {
    label: "Mumbai (Shop + Landmark)",
    text: "Shop No 14, Behind Grand Hotel, Marine Drive, Nariman Point, Mumbai 400021",
  },
  {
    label: "Hyderabad (Tech Park)",
    text: "Tower 3, 5th Floor, Cyber Gateway, Near Hitec City Metro Station, Madhapur, Hyderabad 500081",
  },
  {
    label: "Kolkata (Sector + Block)",
    text: "Plot No 12, Block EP & GP, Near Webel Bhavan, Sector V, Salt Lake, Kolkata, West Bengal 700091",
  },
];

export default function AddressInput({
  address,
  setAddress,
  onParse,
  isLoading,
}) {
  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      onParse();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Search Container */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative group rounded-2xl p-[1px] bg-gradient-to-r from-purple-500/40 via-pink-500/40 to-indigo-500/40 shadow-glow-md"
      >
        <div className="relative rounded-2xl bg-[#141030]/90 backdrop-blur-2xl p-4 sm:p-5">
          <div className="flex items-start gap-3">
            <div className="mt-2 text-purple-400">
              <Search className="w-5 h-5" />
            </div>

            <div className="flex-1 relative">
              <textarea
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type or paste any unstructured Indian address (e.g. 2nd floor, pink building, near ICICI bank, Rajouri Garden, Delhi 110027)..."
                rows={3}
                className="w-full bg-transparent text-white placeholder-white/35 text-base sm:text-lg resize-none outline-none focus:ring-0 leading-relaxed font-sans"
              />
              {address && (
                <button
                  onClick={() => setAddress('')}
                  className="absolute top-0 right-0 p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/10 transition-colors"
                  title="Clear input"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Action Bar */}
          <div className="mt-4 pt-3 border-t border-white/10 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="text-xs text-white/40 flex items-center gap-1.5 hidden sm:flex">
              <span className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-[10px] text-white/60">Ctrl</span>
              <span>+</span>
              <span className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-[10px] text-white/60">Enter</span>
              <span>to parse quickly</span>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onParse}
              disabled={isLoading || !address.trim()}
              className="relative overflow-hidden flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm text-white gradient-accent shadow-glow-sm hover:shadow-glow-md disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Parsing Address...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-pink-200" />
                  <span>Parse Address</span>
                  <CornerDownLeft className="w-3.5 h-3.5 opacity-60 hidden sm:inline" />
                </>
              )}
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Quick Sample Address Chips */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mt-4 flex flex-wrap items-center gap-2"
      >
        <span className="text-xs font-medium text-white/50 flex items-center gap-1 mr-1">
          <MapPin className="w-3 h-3 text-purple-400" /> Try Samples:
        </span>
        {SAMPLE_ADDRESSES.map((sample, idx) => (
          <button
            key={idx}
            onClick={() => setAddress(sample.text)}
            className="text-xs px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 hover:border-purple-500/40 text-white/80 hover:text-white transition-all hover:scale-105 active:scale-95"
          >
            {sample.label}
          </button>
        ))}
      </motion.div>
    </div>
  );
}
