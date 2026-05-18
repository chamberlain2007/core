import { createElement, type ReactNode, type HTMLAttributes } from "react";

export type SplitOptions = {
  charClassName?: string;
  spaceClassName?: string;
};

const SAFE_ATTRS = new Set([
  "class",
  "id",
  "href",
  "title",
  "lang",
  "dir",
  "target",
  "rel",
  "data-",
  "aria-",
]);

function isSafeAttr(name: string): boolean {
  if (SAFE_ATTRS.has(name)) return true;
  return name.startsWith("data-") || name.startsWith("aria-");
}

function reactPropsFromElement(el: Element): Record<string, unknown> {
  const props: Record<string, unknown> = {};
  for (const attr of Array.from(el.attributes)) {
    if (!isSafeAttr(attr.name)) continue;
    if (attr.name === "class") {
      props.className = attr.value;
    } else {
      props[attr.name] = attr.value;
    }
  }
  return props;
}

function splitText(
  text: string,
  keyPrefix: string,
  opts: SplitOptions,
): ReactNode[] {
  const chars = Array.from(text);
  return chars.map((char, i) => {
    const isSpace = /\s/.test(char);
    const className = isSpace ? opts.spaceClassName : opts.charClassName;
    const props: HTMLAttributes<HTMLSpanElement> & {
      "data-char"?: string;
      "data-space"?: string;
    } = { className };
    if (isSpace) {
      props["data-space"] = "true";
    } else {
      props["data-char"] = char;
    }
    return createElement("span", { ...props, key: `${keyPrefix}.${i}` }, char);
  });
}

function splitChildren(
  parent: Node,
  keyPrefix: string,
  opts: SplitOptions,
): ReactNode[] {
  const out: ReactNode[] = [];
  parent.childNodes.forEach((child, i) => {
    const key = `${keyPrefix}.${i}`;
    if (child.nodeType === Node.TEXT_NODE) {
      out.push(...splitText(child.textContent ?? "", key, opts));
    } else if (child.nodeType === Node.ELEMENT_NODE) {
      const el = child as Element;
      const tag = el.tagName.toLowerCase();
      const props = reactPropsFromElement(el);
      out.push(
        createElement(
          tag,
          { ...props, key },
          ...splitChildren(el, key, opts),
        ),
      );
    }
  });
  return out;
}

export function splitHtml(html: string, opts: SplitOptions = {}): ReactNode[] {
  const doc = new DOMParser().parseFromString(
    `<div id="__split-root">${html}</div>`,
    "text/html",
  );
  const root = doc.getElementById("__split-root");
  if (!root) return [];
  return splitChildren(root, "r", opts);
}
