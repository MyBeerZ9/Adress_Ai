import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { motion } from 'framer-motion';
import { MapPin, Navigation, Maximize2, Compass, Layers } from 'lucide-react';

// Custom Neon Pulsing Marker for Leaflet
const createCustomMarker = () => {
  return L.divIcon({
    className: 'custom-pulse-marker',
    html: `
      <div class="pulse-ring"></div>
      <div class="marker-dot"></div>
    `,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
    popupAnchor: [0, -14],
  });
};

// Component to handle map pan & fly animations smoothly
function MapController({ coordinates, zoom = 15 }) {
  const map = useMap();

  useEffect(() => {
    if (coordinates && coordinates.lat && coordinates.lng) {
      map.flyTo([coordinates.lat, coordinates.lng], zoom, {
        animate: true,
        duration: 1.8,
        easeLinearity: 0.25,
      });
    }
  }, [coordinates, zoom, map]);

  return null;
}

export default function MapView({ coordinates, address, components }) {
  const [mapType, setMapType] = useState('dark'); // 'dark' | 'standard' | 'voyager'
  const customIcon = createCustomMarker();

  const lat = coordinates?.lat || 28.6139;
  const lng = coordinates?.lng || 77.2090;

  // Tile layer providers
  const tileLayers = {
    dark: {
      url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      attribution: '&copy; <a href="https://carto.com/">CARTO</a>, OpenStreetMap contributors',
    },
    standard: {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    },
    voyager: {
      url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
      attribution: '&copy; <a href="https://carto.com/">CARTO</a>, OpenStreetMap contributors',
    },
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="glass-card rounded-2xl p-4 sm:p-5 border border-white/10 shadow-glass flex flex-col space-y-4"
    >
      {/* Map Header Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-1">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-pink-500/10 border border-pink-500/20 text-pink-400">
            <Compass className="w-4 h-4 animate-spin-slow" />
          </div>
          <div>
            <h4 className="text-sm sm:text-base font-bold text-white">
              Precise Geospatial Location
            </h4>
            <div className="flex items-center gap-2 text-xs font-mono text-purple-300">
              <span>LAT: {lat.toFixed(5)}</span>
              <span>•</span>
              <span>LNG: {lng.toFixed(5)}</span>
            </div>
          </div>
        </div>

        {/* Tile Layer Selector */}
        <div className="flex items-center gap-1.5 bg-black/30 p-1 rounded-xl border border-white/10">
          <button
            onClick={() => setMapType('dark')}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
              mapType === 'dark'
                ? 'bg-purple-600 text-white shadow-sm'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            Cyber Dark
          </button>
          <button
            onClick={() => setMapType('voyager')}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
              mapType === 'voyager'
                ? 'bg-purple-600 text-white shadow-sm'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            Voyager
          </button>
          <button
            onClick={() => setMapType('standard')}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
              mapType === 'standard'
                ? 'bg-purple-600 text-white shadow-sm'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            OSM Default
          </button>
        </div>
      </div>

      {/* Map Canvas */}
      <div className="relative w-full h-[380px] sm:h-[440px] rounded-xl overflow-hidden border border-white/10 shadow-inner">
        <MapContainer
          center={[lat, lng]}
          zoom={15}
          scrollWheelZoom={false}
          className="w-full h-full"
        >
          <TileLayer
            attribution={tileLayers[mapType].attribution}
            url={tileLayers[mapType].url}
          />

          <MapController coordinates={{ lat, lng }} zoom={15} />

          <Marker position={[lat, lng]} icon={customIcon}>
            <Popup className="custom-leaflet-popup">
              <div className="p-1 space-y-1.5 text-left max-w-[240px]">
                <div className="flex items-center gap-1.5 text-pink-400 font-semibold text-xs uppercase tracking-wider">
                  <MapPin className="w-3.5 h-3.5" />
                  <span>Target Geolocation</span>
                </div>
                <div className="text-xs text-white/90 font-medium leading-snug">
                  {address || 'Target Location'}
                </div>
                <div className="pt-1 border-t border-white/10 text-[10px] font-mono text-purple-300">
                  {lat.toFixed(6)}, {lng.toFixed(6)}
                </div>
              </div>
            </Popup>
          </Marker>
        </MapContainer>

        {/* Live Coordinate Tag */}
        <div className="absolute bottom-3 left-3 z-[400] px-3 py-1.5 rounded-lg bg-[#0f0c29]/80 backdrop-blur-md border border-white/10 text-[11px] font-mono text-white/80 flex items-center gap-1.5 shadow-lg">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>Coordinates: {lat.toFixed(4)}, {lng.toFixed(4)}</span>
        </div>
      </div>
    </motion.div>
  );
}
