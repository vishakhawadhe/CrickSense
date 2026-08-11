import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  
  ArrowRight,
  BarChart3,
  Brain,
  Lock,
  ScanLine,
  ShieldCheck,
  Target,
  TrendingUp,
  UserPlus,
  Video,
} from "lucide-react";
import bowlerImg from "@/assets/hero-bowler.jpg";
import batterImg from "@/assets/hero-batter.jpg";
import galleryAnalysis from "@/assets/gallery-analysis.jpg";
import galleryCoach from "@/assets/gallery-coach.jpg";
import galleryCapture from "@/assets/gallery-capture.jpg";
import galleryTeam from "@/assets/gallery-team.jpg";
import { Nav, Footer, fadeUp } from "@/components/site/chrome";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "CrickSense — AI cricket technique analysis for women" },
      {
        name: "description",
        content:
          "AI-powered bowling and batting analysis built exclusively for women cricketers.",
      },
      { property: "og:title", content: "CrickSense — AI cricket technique analysis for women" },
      {
        property: "og:description",
        content:
          "AI-powered bowling and batting analysis built exclusively for women cricketers.",
      },
    ],
  }),
  component: Landing,
});

function Hero() {
  return (
    <section id="home" className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 grid-bg opacity-70" aria-hidden />
      <div
        className="pointer-events-none absolute -top-40 right-[-10%] h-[520px] w-[520px] rounded-full"
        style={{ background: "radial-gradient(closest-side, color-mix(in oklab, var(--accent) 18%, transparent), transparent)" }}
        aria-hidden
      />
      <div className="container-page relative grid gap-12 py-16 lg:grid-cols-[1.05fr_1fr] lg:gap-16 lg:py-28">
        <motion.div {...fadeUp} className="flex flex-col justify-center">
          <span className="eyebrow">
            <span className="h-1.5 w-1.5 rounded-full bg-accent" />
            AI Cricket Performance Platform
          </span>
          <h1 className="mt-6 text-balance text-5xl font-black leading-[0.95] tracking-tight sm:text-6xl lg:text-[80px]">
            ANALYZE.
            <br />
            IMPROVE.
            <br />
            <span className="text-accent">PERFORM.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg text-muted-foreground">
            AI-powered cricket technique analysis built exclusively for women cricketers.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link to="/features" hash="cta" className="btn-accent">
              Get Started <ArrowRight className="h-4 w-4" />
            </Link>
            <a href="#how" className="btn-ghost">Learn More</a>
          </div>
          <p className="mt-6 flex items-center gap-2 text-sm text-muted-foreground">
            <Lock className="h-3.5 w-3.5" />
            Your videos and data remain private.
          </p>
        </motion.div>

        <motion.div
          {...fadeUp}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          className="relative"
        >
          <div className="grid grid-cols-2 gap-3 sm:gap-4">
            <div className="card-surface overflow-hidden">
              <img
                src={bowlerImg}
                alt="Elite woman fast bowler at ball release"
                className="h-[420px] w-full object-cover sm:h-[560px]"
                width={960}
                height={1408}
              />
            </div>
            <div className="card-surface mt-8 overflow-hidden sm:mt-12">
              <img
                src={batterImg}
                alt="Woman cricket batter playing a cover drive"
                className="h-[420px] w-full object-cover sm:h-[560px]"
                width={960}
                height={1408}
                loading="lazy"
              />
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

const steps = [
  { n: "01", title: "Register", desc: "Create your player profile.", icon: UserPlus },
  { n: "02", title: "Baseline", desc: "Generate personalized benchmarks.", icon: Target },
  { n: "03", title: "Upload Video", desc: "Upload bowling or batting video.", icon: Video },
  { n: "04", title: "AI Analysis", desc: "MediaPipe detects body landmarks and analyzes technique.", icon: Brain },
  { n: "05", title: "Action Score", desc: "Receive performance scores and biomechanical insights.", icon: BarChart3 },
  { n: "06", title: "Track Progress", desc: "Compare sessions and monitor improvement over time.", icon: TrendingUp },
];

function HowItWorks() {
  return (
    <section id="how" className="border-t border-border py-24">
      <div className="container-page">
        <motion.div {...fadeUp} className="max-w-2xl">
          <span className="eyebrow">Workflow</span>
          <h2 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">How it works</h2>
          <p className="mt-4 text-muted-foreground">
            A six-step pipeline from your first upload to measurable technique gains.
          </p>
        </motion.div>
        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {steps.map((s, i) => (
            <motion.div
              {...fadeUp}
              transition={{ duration: 0.5, delay: i * 0.05, ease: [0.22, 1, 0.36, 1] }}
              key={s.n}
              className="card-surface card-hover p-6"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold tracking-widest text-muted-foreground">{s.n}</span>
                <span className="grid h-9 w-9 place-items-center rounded-full bg-accent/10 text-accent">
                  <s.icon className="h-4 w-4" />
                </span>
              </div>
              <h3 className="mt-6 text-lg font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

const builtFor = [
  { title: "Personalized Analysis", desc: "Benchmarks generated specifically for women players.", icon: Target },
  { title: "AI Pose Detection", desc: "MediaPipe detects key body landmarks for biomechanical analysis.", icon: ScanLine },
  { title: "Privacy First", desc: "Player videos and information remain secure.", icon: ShieldCheck },
  { title: "Progress Tracking", desc: "Monitor technique improvements across every session.", icon: TrendingUp },
];

function BuiltForWomen() {
  return (
    <section className="border-t border-border py-24">
      <div className="container-page">
        <motion.div {...fadeUp} className="max-w-3xl">
          <span className="eyebrow">Purpose-built</span>
          <h2 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Built for women cricketers
          </h2>
          <p className="mt-4 text-muted-foreground">
            Designed around female biomechanics instead of adapting men's cricket models.
          </p>
        </motion.div>
        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {builtFor.map((f, i) => (
            <motion.div
              {...fadeUp}
              transition={{ duration: 0.5, delay: i * 0.05, ease: [0.22, 1, 0.36, 1] }}
              key={f.title}
              className="card-surface card-hover p-6"
            >
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-accent/10 text-accent">
                <f.icon className="h-5 w-5" />
              </span>
              <h3 className="mt-6 text-lg font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{f.desc}</p>
            </motion.div>
          ))}
        </div>
        <div className="mt-14 flex justify-center">
          <Link to="/features" className="btn-accent">
            Explore all features <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </section>
  );
}

const gallery = [
  {
    src: galleryAnalysis,
    title: "Pose detection in action",
    caption: "Reviewing bowling biomechanics on the CrickSense dashboard.",
    span: "lg:col-span-2 lg:row-span-2",
    ratio: "aspect-[4/5] lg:aspect-auto lg:h-full",
  },
  {
    src: galleryCapture,
    title: "Capture at the crease",
    caption: "A single phone on a tripod is all it takes to record a session.",
    span: "",
    ratio: "aspect-[4/3]",
  },
  {
    src: galleryCoach,
    title: "Coach & player, side by side",
    caption: "Personalized feedback delivered right at the nets.",
    span: "",
    ratio: "aspect-[4/3]",
  },
  {
    src: galleryTeam,
    title: "Team-wide insight",
    caption: "Squads compare sessions and track collective progress.",
    span: "lg:col-span-2",
    ratio: "aspect-[16/9]",
  },
];

function Gallery() {
  return (
    <section id="gallery" className="border-t border-border py-24">
      <div className="container-page">
        <motion.div {...fadeUp} className="max-w-2xl">
          <span className="eyebrow">In the field</span>
          <h2 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            CrickSense in action
          </h2>
          <p className="mt-4 text-muted-foreground">
            Real moments from athletes, coaches and academies using CrickSense to
            sharpen technique.
          </p>
        </motion.div>
        <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-4 lg:grid-rows-2">
          {gallery.map((g, i) => (
            <motion.figure
              {...fadeUp}
              transition={{ duration: 0.55, delay: i * 0.06, ease: [0.22, 1, 0.36, 1] }}
              key={g.title}
              className={`group card-surface relative overflow-hidden ${g.span}`}
            >
              <img
                src={g.src}
                alt={g.title}
                loading="lazy"
                width={1024}
                height={1024}
                className={`w-full object-cover transition-transform duration-700 ease-out group-hover:scale-105 ${g.ratio}`}
              />
              <div
                className="pointer-events-none absolute inset-0 bg-gradient-to-t from-background/90 via-background/10 to-transparent opacity-90"
                aria-hidden
              />
              <figcaption className="absolute inset-x-0 bottom-0 p-5">
                <div className="text-sm font-semibold">{g.title}</div>
                <div className="mt-1 text-xs text-muted-foreground">{g.caption}</div>
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </div>
    </section>
  );
}

function Landing() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Nav />
      <main>
        <Hero />
        <HowItWorks />
        <BuiltForWomen />
        <Gallery />
      </main>
      <Footer />
    </div>
  );
}
