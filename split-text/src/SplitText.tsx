import { createElement, useMemo, type JSX } from "react";
import { splitHtml } from "./splitNode";
import styles from "./SplitText.module.css";

export type SplitTextProps = {
  /**
   * Trusted HTML string. Inline tags (e.g. <strong>, <em>, <a>) are preserved
   * around the per-character spans. Callers must sanitize untrusted input
   * before passing it here.
   */
  html: string;
  /** Wrapper tag. Defaults to "span" so the component is inline by default. */
  as?: keyof JSX.IntrinsicElements;
  /** className applied to the outer wrapper. */
  className?: string;
  /** className applied to each non-whitespace character span. */
  charClassName?: string;
  /** className applied to each whitespace character span. */
  spaceClassName?: string;
};

export function SplitText({
  html,
  as = "span",
  className,
  charClassName,
  spaceClassName,
}: SplitTextProps): JSX.Element {
  const splitChildren = useMemo(
    () =>
      splitHtml(html, {
        charClassName: [styles.char, charClassName].filter(Boolean).join(" "),
        spaceClassName: [styles.space, spaceClassName].filter(Boolean).join(" "),
      }),
    [html, charClassName, spaceClassName],
  );

  const wrapperClass = [styles.wrapper, className].filter(Boolean).join(" ");

  return createElement(
    as,
    { className: wrapperClass, "data-split-text": "" },
    createElement("span", {
      className: styles.sr,
      "data-split-text-sr": "",
      dangerouslySetInnerHTML: { __html: html },
    }),
    createElement(
      "span",
      {
        className: styles.visual,
        "data-split-text-visual": "",
        "aria-hidden": "true",
        // `inert` keeps the split spans out of focus order & user selection.
        inert: "",
      },
      ...splitChildren,
    ),
  );
}
