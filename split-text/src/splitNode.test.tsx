import { describe, it, expect } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { splitHtml } from "./splitNode";

function render(html: string, opts = {}) {
  return renderToStaticMarkup(<>{splitHtml(html, opts)}</>);
}

describe("splitHtml", () => {
  it("wraps each character in its own span", () => {
    const out = render("Hi");
    const matches = out.match(/<span[^>]*data-char="[^"]"[^>]*>./g) ?? [];
    expect(matches).toHaveLength(2);
    expect(out).toContain('data-char="H"');
    expect(out).toContain('data-char="i"');
  });

  it("emits space spans for whitespace, not data-char spans", () => {
    const out = render("a b");
    expect(out).toContain('data-char="a"');
    expect(out).toContain('data-space="true"');
    expect(out).toContain('data-char="b"');
    expect(out).not.toMatch(/data-char=" "/);
  });

  it("preserves nested inline tags around split characters", () => {
    const out = render("Hi <strong>bold</strong>!");
    expect(out).toMatch(
      /<strong><span[^>]*data-char="b"[^>]*>b<\/span>.*<\/strong>/,
    );
    expect(out).toContain('data-char="!"');
  });

  it("treats emoji as one character (grapheme-aware-ish)", () => {
    const out = render("a😀b");
    const charSpans = out.match(/data-char="[^"]+"/g) ?? [];
    expect(charSpans).toHaveLength(3);
    expect(out).toContain('data-char="😀"');
  });

  it("applies provided char and space class names", () => {
    const out = render("a b", {
      charClassName: "x-char",
      spaceClassName: "x-space",
    });
    expect(out).toContain('class="x-char"');
    expect(out).toContain('class="x-space"');
  });

  it("passes through safe attributes on inline tags", () => {
    const out = render(
      '<a href="https://example.com" title="t" rel="noopener">go</a>',
    );
    expect(out).toContain('href="https://example.com"');
    expect(out).toContain('title="t"');
    expect(out).toContain('rel="noopener"');
  });

  it("drops unsafe attributes like onclick", () => {
    const out = render('<span onclick="alert(1)">x</span>');
    expect(out).not.toContain("onclick");
    expect(out).toContain('data-char="x"');
  });

  it("ignores comment nodes", () => {
    const out = render("a<!-- c -->b");
    expect(out).not.toContain("<!--");
    const charSpans = out.match(/data-char="[^"]+"/g) ?? [];
    expect(charSpans).toHaveLength(2);
  });

  it("returns empty array for empty input", () => {
    expect(splitHtml("")).toEqual([]);
  });
});
