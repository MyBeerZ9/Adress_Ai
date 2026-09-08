import React from 'react';
import { motion } from 'framer-motion';
import {
  Home,
  Navigation,
  Compass,
  MapPin,
  Building2,
  Globe2,
  Hash,
  CheckCircle,
  ShieldCheck,
  Zap,
  Copy,
  Check,
} from 'lucide-react';

export default function ParsedCard({ result, onCopyFormatted, isCopied }) {
  if (!result) return null;

  const {
    structured_components: sc,
    confidence_score: score,
    formatted_address,
    provider,
    landmark_detected,
  } = result;

  const scorePercent = Math.round(score * 100);

  // Confidence color rating
  const getScoreColor = (p) => {
    if (p >= 80) return { ring: 'stroke-emerald-400', text: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30', label: 'High Precision' };
    if (p >= 50) return { ring: 'stroke-amber-400', text: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/30', label: 'Moderate Confidence' };
    return { ring: 'stroke-pink-400', text: 'text-pink-400', bg: 'bg-pink-500/10 border-pink-500/30', label: 'Basic Resolution' };
  };

  const scoreMeta = getScoreColor(scorePercent);

  // Circular gauge calculations
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (scorePercent / 100) * circumference;

  const componentItems = [
    {
      label: 'House / Building / Floor',
      value: sc.house_number,
      icon: <Home className="w-4 h-4 text-purple-400" />,
      color: 'border-purple-500/20 bg-purple-500/5',
    },
    {
      label: 'Street / Road',
      value: sc.street,
      icon: <Navigation className="w-4 h-4 text-indigo-400" />,
      color: 'border-indigo-500/20 bg-indigo-500/5',
    },
    {
      label: 'Prominent Landmark',
      value: sc.landmark || landmark_detected,
      icon: <Compass className="w-4 h-4 text-pink-400" />,
      color: 'border-pink-500/30 bg-pink-500/10 shadow-sm shadow-pink-500/10',
      highlight: true,
    },
    {
      label: 'Sublocality / Sector',
      value: sc.sublocality,
      icon: <Building2 className="w-4 h-4 text-cyan-400" />,
      color: 'border-cyan-500/20 bg-cyan-500/5',
    },
    {
      label: 'Locality / Area',
      value: sc.locality,
      icon: <MapPin className="w-4 h-4 text-emerald-400" />,
      color: 'border-emerald-500/20 bg-emerald-500/5',
    },
    {
      label: 'City',
      value: sc.city,
      icon: <Building2 className="w-4 h-4 text-amber-400" />,
      color: 'border-amber-500/20 bg-amber-500/5',
    },
    {
      label: 'State',
      value: sc.state,
      icon: <Globe2 className="w-4 h-4 text-blue-400" />,
      color: 'border-blue-500/20 bg-blue-500/5',
    },
    {
      label: 'PIN Code',
      value: sc.postal_code,
      icon: <Hash className="w-4 h-4 text-rose-400" />,
      color: 'border-rose-500/20 bg-rose-500/5',
    },
    {
      label: 'Country',
      value: sc.country || 'India',
      icon: <Globe2 className="w-4 h-4 text-teal-400" />,
      color: 'border-teal-500/20 bg-teal-500/5',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <div className="space-y-6">
      {/* Header Info & Confidence Meter */}
      <div className="glass-card rounded-2xl p-5 sm:p-6 flex flex-col md:flex-row items-center justify-between gap-6 border border-white/10 shadow-glass">
        {/* Left info */}
        <div className="space-y-2 text-center md:text-left flex-1">
          <div className="flex flex-wrap items-center justify-center md:justify-start gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5" />
              Parsed Successfully
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-white/5 text-white/70 border border-white/10 uppercase tracking-wider">
              Source: {provider}
            </span>
          </div>

          <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Structured Address Breakdown
          </h3>
          <p className="text-sm text-white/60">
            Components segmented and normalized from unstructured input
          </p>
        </div>

        {/* Confidence Gauge */}
        <div className="flex items-center gap-4 px-5 py-3 rounded-2xl bg-[#0f0c29]/60 border border-white/10">
          <div className="relative w-20 h-20 flex items-center justify-center">
            <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 96 96">
              <circle
                cx="48"
                cy="48"
                r={radius}
                className="stroke-white/10"
                strokeWidth="7"
                fill="transparent"
              />
              <motion.circle
                cx="48"
                cy="48"
                r={radius}
                className={scoreMeta.ring}
                strokeWidth="7"
                strokeDasharray={circumference}
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset }}
                transition={{ duration: 1.2, ease: "easeOut" }}
                strokeLinecap="round"
                fill="transparent"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-lg font-bold text-white tracking-tighter">
                {scorePercent}%
              </span>
            </div>
          </div>

          <div>
            <div className="text-xs uppercase tracking-wider font-semibold text-white/40">
              Confidence
            </div>
            <div className={`text-sm font-semibold ${scoreMeta.text}`}>
              {scoreMeta.label}
            </div>
            <div className="text-[11px] text-white/50">
              {score >= 0.8 ? 'High Component Coverage' : 'Standard Resolution'}
            </div>
          </div>
        </div>
      </div>

      {/* Formatted Address Banner */}
      <div className="glass-card rounded-xl p-4 border border-white/10 flex items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <MapPin className="w-5 h-5 text-purple-400 mt-0.5 shrink-0" />
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-white/40">
              Standardized Formatted Address
            </div>
            <div className="text-sm sm:text-base text-white font-medium mt-0.5">
              {formatted_address}
            </div>
          </div>
        </div>

        <button
          onClick={onCopyFormatted}
          className="shrink-0 p-2 sm:px-3 sm:py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white/80 hover:text-white text-xs font-medium flex items-center gap-1.5 transition-all active:scale-95"
          title="Copy formatted address"
        >
          {isCopied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden sm:inline text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Structured Components Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5"
      >
        {componentItems.map((item, idx) => (
          <motion.div
            key={idx}
            variants={itemVariants}
            className={`glass-card glass-card-hover rounded-xl p-4 border ${item.color} relative overflow-hidden`}
          >
            {item.highlight && (
              <div className="absolute top-0 right-0 px-2 py-0.5 bg-pink-500/20 text-pink-300 text-[10px] font-bold rounded-bl-lg border-b border-l border-pink-500/30">
                Landmark Match
              </div>
            )}
            <div className="flex items-center gap-2 mb-1.5">
              <div className="p-1.5 rounded-lg bg-white/5">
                {item.icon}
              </div>
              <span className="text-xs font-medium text-white/50">
                {item.label}
              </span>
            </div>
            <div className="text-sm sm:text-base font-semibold text-white truncate pl-1">
              {item.value ? (
                <span>{item.value}</span>
              ) : (
                <span className="text-white/20 italic font-normal text-xs">
                  Not specified in address
                </span>
              )}
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
