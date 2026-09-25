import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Activity, ArrowRight, BarChart3, ScanLine, Target } from "lucide-react";
import bowlerImg from "@/assets/hero-bowler.jpg";
import batterImg from "@/assets/hero-batter.jpg";
import { Nav, Footer, fadeUp } from "@/components/site/chrome";

export const Route = createFileRoute("/features")({
  head: () => ({
    meta: [
      { title: "Features — CrickSense" },
      {
        name: "description",
        content:
          "Pose detection, biomechanics analysis, personalized benchmarks and a performance dashboard for women cricketers.",
      },
      { property: "og:title", content: "Features — CrickSense" },
      {
        property: "og:description",
        content:
          "Explore CrickSense features: AI pose detection, biomechanics, personalized benchmarks, and dashboards.",
      },
    ],
  }),
  component: FeaturesPage,
});

const features = [
  {
    eyebrow: "Feature 01",
    title: "AI Pose Detection",
    desc: "MediaPipe reconstructs your action frame by frame from standard phone video.",
    image: bowlerImg,
    bullets: ["Frame-by-frame skeleton", "Real-time landmark tracking", "Works on standard phone video"],
    icon: ScanLine,
  },
  {
    eyebrow: "Feature 02",
    title: "Biomechanics Analysis",
    desc: "Quantify the mechanics that define elite technique.",
    image: batterImg,
    bullets: ["Elbow angle", "Knee angle", "Stride length", "Release point", "Balance", "Follow-through"],
    icon: Activity,
  },
  {
    eyebrow: "Feature 03",
    title: "Personalized Benchmarks",
    desc: "Expected values generated from your height, age and bowling style instead of one universal standard.",
    image: bowlerImg,
    bullets: ["Height", "Age", "Bowling style"],
    icon: Target,
  },
  {
    eyebrow: "Feature 04",
    title: "Performance Dashboard",
    desc: "A clean dashboard to visualize scores, historical progress and session comparisons.",
    image: batterImg,
    bullets: ["Action Scores", "Historical Progress", "Session Comparisons", "Technique Improvements"],
    icon: BarChart3,
  },
];

function FeaturesHeader() {
  return (
    <section className="relative overflow-hidden border-b border-border">
      <div className="pointer-events-none absolute inset-0 grid-bg opacity-60" aria-hidden />
      <div className="container-page relative py-20 lg:py-28">
        <motion.div {...fadeUp} className="max-w-3xl">
          <span className="eyebrow">Features</span>
          <h1 className="mt-4 text-5xl font-black tracking-tight sm:text-6xl">
            Everything you need to measure the invisible.
          </h1>
          <p className="mt-6 max-w-xl text-lg text-muted-foreground">
            The tools inside CrickSense — from pose detection to your personal performance dashboard.
          </p>
        </motion.div>
      </div>
    </section>
  );
}

function FeatureBlocks() {
  return (
    <section className="py-24">
      <div className="container-page flex flex-col gap-24">
        {features.map((f, i) => (
          <motion.div
            {...fadeUp}
            key={f.title}
            className={`grid items-center gap-10 lg:grid-cols-2 lg:gap-16 ${
              i % 2 === 1 ? "lg:[&>*:first-child]:order-2" : ""
            }`}
          >
            <div className="card-surface overflow-hidden">
              <img
                src={f.image}
                alt=""
                className="h-[380px] w-full object-cover sm:h-[460px]"
                loading="lazy"
              />
            </div>
            <div>
              <span className="eyebrow">{f.eyebrow}</span>
              <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">{f.title}</h2>
              <p className="mt-4 max-w-lg text-muted-foreground">{f.desc}</p>
              <ul className="mt-6 grid gap-2 sm:grid-cols-2">
                {f.bullets.map((b) => (
                  <li key={b} className="flex items-center gap-2 text-sm">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                    {b}
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

const testimonials = [
  {
    quote:
      "CrickSense showed me exactly what my release point was doing under fatigue. My line has never been more consistent.",
    name: "Fast Bowler",
    role: "State-level player",
  },
  {
    quote:
      "The benchmarks are actually tuned to me, not to a men's dataset. Finally, feedback that reflects my game.",
    name: "All-rounder",
    role: "Club captain",
  },
  {
    quote:
      "I compare every net session now. The dashboard makes technique work feel measurable instead of vague.",
    name: "Top-order batter",
    role: "Academy player",
  },
];

function Testimonials() {
  return (
    <section className="border-t border-border py-24">
      <div className="container-page">
        <motion.div {...fadeUp} className="max-w-2xl">
          <span className="eyebrow">Trusted by players</span>
          <h2 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            From the players using it.
          </h2>
        </motion.div>
        <div className="mt-14 grid gap-5 md:grid-cols-3">
          {testimonials.map((t, i) => (
            <motion.blockquote
              {...fadeUp}
              transition={{ duration: 0.5, delay: i * 0.05, ease: [0.22, 1, 0.36, 1] }}
              key={t.name}
              className="card-surface flex flex-col justify-between p-6"
            >
              <p className="text-base leading-relaxed">"{t.quote}"</p>
              <footer className="mt-8 flex items-center gap-3 border-t border-border pt-4">
                <span className="grid h-9 w-9 place-items-center rounded-full bg-accent/15 text-accent text-xs font-semibold">
                  {t.name[0]}
                </span>
                <div>
                  <div className="text-sm font-semibold">{t.name}</div>
                  <div className="text-xs text-muted-foreground">{t.role}</div>
                </div>
              </footer>
            </motion.blockquote>
          ))}
        </div>
      </div>
    </section>
  );
}

function About() {
  return (
    <section id="about" className="border-t border-border py-24">
      <div className="container-page grid gap-10 lg:grid-cols-2 lg:gap-20">
        <motion.div {...fadeUp}>
          <span className="eyebrow">About</span>
          <h2 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            A performance lab in every player's pocket.
          </h2>
        </motion.div>
        <motion.div {...fadeUp} className="flex flex-col justify-center gap-4 text-muted-foreground">
          <p>
            CrickSense is built by engineers and coaches who believe women's cricket deserves
            dedicated technology — not repurposed models trained on the men's game.
          </p>
          <p>
            Every metric, benchmark and recommendation is calibrated to the female athlete, from
            release biomechanics to shot execution.
          </p>
        </motion.div>
      </div>
    </section>
  );
}

function CTA() {
  return (
    <section id="cta" className="border-t border-border py-28">
      <div className="container-page">
        <motion.div
          {...fadeUp}
          className="card-surface relative overflow-hidden px-8 py-16 text-center sm:px-16 sm:py-24"
        >
          <div className="pointer-events-none absolute inset-0 grid-bg opacity-60" aria-hidden />
          <div
            className="pointer-events-none absolute -bottom-32 left-1/2 h-[420px] w-[420px] -translate-x-1/2 rounded-full"
            style={{ background: "radial-gradient(closest-side, color-mix(in oklab, var(--accent) 22%, transparent), transparent)" }}
            aria-hidden
          />
          <div className="relative">
            <h2 className="mx-auto max-w-3xl text-balance text-4xl font-bold tracking-tight sm:text-6xl">
              Ready to improve your game?
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-muted-foreground">
              Upload your first video and get biomechanical insights in minutes.
            </p>
            <div className="mt-8 flex justify-center">
              <a href="#" className="btn-accent">
                Start Your Analysis <ArrowRight className="h-4 w-4" />
              </a>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function FeaturesPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Nav />
      <main>
        <FeaturesHeader />
        <FeatureBlocks />
        <Testimonials />
        <About />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}
