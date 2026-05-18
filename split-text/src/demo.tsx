import { SplitText } from "./SplitText";

const demoCss = `
  .demo {
    font-family: system-ui, sans-serif;
    max-width: 40rem;
    margin: 4rem auto;
    padding: 0 1rem;
    line-height: 1.4;
  }
  .demo h1 { font-size: 2.5rem; margin: 0 0 1.5rem; }
  .demo p { font-size: 1.25rem; }
  .stagger [data-char],
  .stagger [data-space] {
    opacity: 0;
    transform: translateY(0.3em);
    animation: rise 0.6s forwards;
  }
  .stagger [data-char]:nth-child(n)  { animation-delay: calc(var(--i, 0) * 30ms); }
  @keyframes rise { to { opacity: 1; transform: none; } }
`;

export function Demo() {
  return (
    <main className="demo">
      <style>{demoCss}</style>
      <h1>
        <SplitText
          className="stagger"
          html="Hello, <strong>accessible</strong> world!"
        />
      </h1>
      <p>
        VoiceOver should announce the headline as a single phrase, including the
        emphasis on <em>accessible</em>, despite each glyph being its own span.
      </p>
      <p>
        <SplitText html="Try selecting this text &mdash; only the screen-reader copy is selectable; the visual split layer is inert." />
      </p>
    </main>
  );
}
