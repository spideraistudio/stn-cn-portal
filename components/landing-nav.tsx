"use client";
import { useState } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";

const navLinks = [
  { href: "/about", label: "About" },
  { href: "/plans", label: "Plans" },
  { href: "/faq", label: "FAQ" },
  { href: "/contact", label: "Contact" },
  { href: "/login", label: "Member login" },
  { href: "/admin-login", label: "Admin", muted: true },
];

export function LandingNav() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="relative z-20 mx-auto flex max-w-6xl items-center justify-between px-5 py-5">
      {/* Logo */}
      <Link href="/home" className="flex items-center gap-3">
        <span className="grid size-11 place-items-center rounded-xl bg-white/10 backdrop-blur-md ring-1 ring-white/20">
          <span className="text-sm font-bold text-amber-300">STN</span>
        </span>
        <span className="text-lg font-semibold text-white">Sellers Trust Network</span>
      </Link>

      {/* Desktop nav */}
      <div className="hidden items-center gap-1 md:flex">
        {navLinks.map(link => (
          <Link
            key={link.href}
            href={link.href}
            className={`rounded-lg px-4 py-2 text-sm font-semibold transition hover:bg-white/10 ${link.muted ? "text-white/70 hover:text-white" : "text-white/90"}`}
          >
            {link.label}
          </Link>
        ))}
      </div>

      {/* Mobile hamburger */}
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
        className="grid size-11 place-items-center rounded-lg text-white transition hover:bg-white/10 md:hidden"
        aria-label={open ? "Close menu" : "Open menu"}
        aria-expanded={open}
      >
        {open ? <X className="size-6" /> : <Menu className="size-6" />}
      </button>

      {/* Mobile menu dropdown */}
      {open && (
        <div className="absolute left-0 right-0 top-full mx-5 origin-top overflow-hidden rounded-2xl border border-white/15 bg-[#15388c]/95 shadow-2xl backdrop-blur-xl md:hidden">
          <div className="flex flex-col p-2">
            {navLinks.map(link => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className={`rounded-lg px-4 py-3 text-sm font-semibold transition hover:bg-white/10 ${link.muted ? "text-white/70" : "text-white"}`}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
