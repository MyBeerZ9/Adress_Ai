import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Code, Copy, Check, Download, Terminal, ChevronDown, ChevronUp } from 'lucide-react';

export default function JsonViewer({ data, onCopy, isCopied }) {
  const [activeTab, setActiveTab] = useState('json'); // 'json' | 'curl'
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (!data) return null;

  const jsonString = JSON.stringify(data, null, 2);

  const curlCommand = `curl -X POST "http://localhost:8000/parse" \\
  -H "Content-Type: application/json" \\
  -d '{"address": "${(data.original_address || '').replace(/'/g, "\\'")}"}'`;

  const handleDownload = () => {
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `addressai-parsed-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-glass"
    >
      {/* Header Tabs & Actions */}
      <div className="px-4 py-3 bg-[#120e36]/80 border-b border-white/10 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-black/40 p-1 rounded-xl border border-white/10">
            <button
              onClick={() => setActiveTab('json')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'json'
                  ? 'bg-purple-600 text-white shadow-sm'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
            >
              <Code className="w-3.5 h-3.5" />
              <span>Parsed JSON</span>
            </button>
            <button
              onClick={() => setActiveTab('curl')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'curl'
                  ? 'bg-purple-600 text-white shadow-sm'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>cURL Snippet</span>
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onCopy(activeTab === 'json' ? jsonString : curlCommand)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white/90 hover:text-white text-xs font-medium transition-all active:scale-95 shadow-sm"
          >
            {isCopied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy {activeTab === 'json' ? 'JSON' : 'cURL'}</span>
              </>
            )}
          </button>

          {activeTab === 'json' && (
            <button
              onClick={handleDownload}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white/90 hover:text-white text-xs font-medium transition-all active:scale-95 shadow-sm"
              title="Download JSON File"
            >
              <Download className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Download</span>
            </button>
          )}

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-white/50 hover:text-white hover:bg-white/5 transition-colors"
            title={isCollapsed ? 'Expand viewer' : 'Collapse viewer'}
          >
            {isCollapsed ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronUp className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Code Container */}
      <AnimatePresence>
        {!isCollapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="p-4 bg-[#0a071f]/80 overflow-x-auto max-h-[360px] font-mono text-xs sm:text-sm text-purple-200 leading-relaxed"
          >
            <pre className="selection:bg-purple-500/40">
              <code>{activeTab === 'json' ? jsonString : curlCommand}</code>
            </pre>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
