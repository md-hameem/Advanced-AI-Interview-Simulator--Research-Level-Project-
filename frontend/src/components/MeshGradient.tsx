"use client";

export default function MeshGradient() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      {/* Deep black base */}
      <div className="absolute inset-0 bg-black" />

      {/* Blob 1 — Indigo, top-right */}
      <div
        className="mesh-blob-1 absolute -top-[20%] -right-[10%] w-[60vw] h-[60vw] rounded-full opacity-[0.07]"
        style={{
          background: "radial-gradient(circle, #6366f1 0%, transparent 70%)",
          filter: "blur(120px)",
        }}
      />

      {/* Blob 2 — Cyan, bottom-left */}
      <div
        className="mesh-blob-2 absolute -bottom-[10%] -left-[15%] w-[50vw] h-[50vw] rounded-full opacity-[0.05]"
        style={{
          background: "radial-gradient(circle, #22d3ee 0%, transparent 70%)",
          filter: "blur(100px)",
        }}
      />

      {/* Blob 3 — Purple, center */}
      <div
        className="mesh-blob-3 absolute top-[40%] left-[30%] w-[40vw] h-[40vw] rounded-full opacity-[0.04]"
        style={{
          background: "radial-gradient(circle, #a855f7 0%, transparent 70%)",
          filter: "blur(140px)",
        }}
      />

      {/* Subtle noise texture overlay */}
      <div
        className="absolute inset-0 opacity-[0.015]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
        }}
      />
    </div>
  );
}
