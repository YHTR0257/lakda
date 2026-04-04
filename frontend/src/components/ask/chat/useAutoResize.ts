"use client";

import { useEffect, useRef } from "react";

/**
 * textarea を入力内容に合わせて自動リサイズする hook。
 * - 1行: 1行高
 * - 2行: 2行高
 * - 3行以上: 2行高で overflow-y: auto スクロール
 */
export function useAutoResize(value: string) {
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const style = getComputedStyle(el);
    const lineHeight = parseFloat(style.lineHeight);
    const paddingY = parseFloat(style.paddingTop) + parseFloat(style.paddingBottom);
    const maxHeight = lineHeight * 2 + paddingY;
    el.style.height = "auto";
    const next = Math.min(el.scrollHeight, maxHeight);
    el.style.height = `${next}px`;
    el.style.overflowY = el.scrollHeight > maxHeight ? "auto" : "hidden";
  }, [value]);

  return ref;
}
