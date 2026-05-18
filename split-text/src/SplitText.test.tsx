import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import { SplitText } from "./SplitText";

describe("<SplitText />", () => {
  it("renders an accessible copy that exposes the full text to assistive tech", () => {
    const { container } = render(
      <SplitText html="Hello, <strong>accessible</strong> world!" />,
    );
    const sr = container.querySelector("[data-split-text-sr]");
    expect(sr).not.toBeNull();
    // Full unbroken text is present for the accessibility tree.
    expect(sr!.textContent).toBe("Hello, accessible world!");
    // Nested semantics are preserved on the accessible copy.
    expect(sr!.querySelector("strong")).not.toBeNull();
  });

  it("marks the visual split copy as hidden from assistive tech and inert", () => {
    const { container } = render(<SplitText html="Hi there" />);
    const visual = container.querySelector("[data-split-text-visual]");
    expect(visual).not.toBeNull();
    expect(visual!.getAttribute("aria-hidden")).toBe("true");
    expect(visual!.hasAttribute("inert")).toBe(true);
  });

  it("produces a span per character (including spaces) in the visual copy", () => {
    const { container } = render(<SplitText html="ab cd" />);
    const visual = container.querySelector("[data-split-text-visual]")!;
    const chars = visual.querySelectorAll("[data-char]");
    const spaces = visual.querySelectorAll("[data-space]");
    expect(chars).toHaveLength(4);
    expect(spaces).toHaveLength(1);
  });

  it("does not use display:none or visibility:hidden for the accessible copy", () => {
    // These would remove the node from the accessibility tree on all major
    // screen readers and defeat the purpose of the duplicate-and-hide pattern.
    const { container } = render(<SplitText html="hi" />);
    const sr = container.querySelector("[data-split-text-sr]") as HTMLElement;
    const style = sr.getAttribute("style") ?? "";
    expect(style).not.toMatch(/display\s*:\s*none/);
    expect(style).not.toMatch(/visibility\s*:\s*hidden/);
  });

  it("has no axe-detectable accessibility violations", async () => {
    const { container } = render(
      <main>
        <h1>
          <SplitText html="Hello, <strong>accessible</strong> world!" />
        </h1>
      </main>,
    );
    const results = await axe(container);
    expect(results.violations).toEqual([]);
  });
});
