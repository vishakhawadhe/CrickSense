import { Link } from "@tanstack/react-router";
import { Activity, ArrowRight, Camera, Github, Linkedin, Menu, Moon, Sun, X } from "lucide-react";
import { useState } from "react";
import { useTheme } from "@/lib/theme";

export function Logo() {
  return (
    <Link to="/" className="flex items-center gap-2">
      <span className="grid h-8 w-8 place-items-center rounded-lg bg-accent text-accent-foreground">
        <Activity className="h-4 w-4" strokeWidth={2.5} />
      </span>
      <span className="text-[17px] font-semibold tracking-tight">CrickSense</span>
    </Link>
  );
}

function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button
      onClick={toggle}
      aria-label="Toggle theme"
      className="grid h-10 w-10 place-items-center rounded-full border border-border text-foreground/80 transition hover:bg-foreground/5"
    >
      {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  );
}

const navLinks = [
  { to: "/", label: "Home" },
  { to: "/features", label: "Features" },
] as const;

export function Nav() {
  const [open, setOpen] = useState(false);
  return (
    <header
      className="sticky top-0 z-50 border-b border-border/80 backdrop-blur-xl"
      style={{ backgroundColor: "color-mix(in oklab, var(--background) 80%, transparent)" }}
    >
      <div className="container-page flex h-16 items-center justify-between">
        <Logo />
        <nav className="hidden items-center gap-8 md:flex">
          {navLinks.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className="text-sm text-muted-foreground transition hover:text-foreground"
              activeProps={{ className: "text-sm text-foreground" }}
              activeOptions={{ exact: true }}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="hidden items-center gap-2 md:flex">
          <ThemeToggle />
          <Link to="/login" className="btn-ghost text-sm">Login</Link>
          <Link to="/features" hash="cta" className="btn-accent text-sm">
            Get Started <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle />
          <button
            onClick={() => setOpen((v) => !v)}
            className="grid h-10 w-10 place-items-center rounded-full border border-border"
            aria-label="Menu"
          >
            {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>
      {open && (
        <div className="border-t border-border md:hidden">
          <div className="container-page flex flex-col gap-1 py-4">
            {navLinks.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setOpen(false)}
                className="rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-foreground/5 hover:text-foreground"
              >
                {l.label}
              </Link>
            ))}
            <div className="mt-2 flex gap-2 px-1">
              <Link to="/login" onClick={() => setOpen(false)} className="btn-ghost flex-1 text-sm">Login</Link>
              <Link to="/features" hash="cta" onClick={() => setOpen(false)} className="btn-accent flex-1 text-sm">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

function FooterCol({ title, links }: { title: string; links: string[] }) {
  return (
    <div>
      <div className="text-sm font-semibold">{title}</div>
      <ul className="mt-4 space-y-2">
        {links.map((l) => (
          <li key={l}>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground">{l}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function Footer() {
  return (
    <footer id="contact" className="border-t border-border py-14">
      <div className="container-page">
        <div className="grid gap-10 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
          <div>
            <Logo />
            <p className="mt-4 max-w-xs text-sm text-muted-foreground">
              AI cricket technique analysis built for women cricketers.
            </p>
          </div>
          <FooterCol title="Product" links={["Features", "How It Works", "Pricing"]} />
          <FooterCol title="Company" links={["About", "Contact", "Privacy Policy"]} />
          <div>
            <div className="text-sm font-semibold">Connect</div>
            <div className="mt-4 flex gap-2">
              <a className="grid h-9 w-9 place-items-center rounded-full border border-border hover:bg-foreground/5" href="#" aria-label="GitHub">
                <Github className="h-4 w-4" />
              </a>
              <a className="grid h-9 w-9 place-items-center rounded-full border border-border hover:bg-foreground/5" href="#" aria-label="LinkedIn">
                <Linkedin className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>
        <div className="mt-12 flex flex-col items-start justify-between gap-3 border-t border-border pt-6 text-xs text-muted-foreground sm:flex-row sm:items-center">
          <span>© {new Date().getFullYear()} CrickSense. All rights reserved.</span>
          <span className="flex items-center gap-2">
            <Camera className="h-3.5 w-3.5" /> Powered by MediaPipe & AI
          </span>
        </div>
      </div>
    </footer>
  );
}

export const fadeUp = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" },
  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] as const },
};
