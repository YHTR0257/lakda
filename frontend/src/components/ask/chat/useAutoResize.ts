"use client";

import { useEffect, useRef } from "react";

/**
 * textarea を入力内容に合わせて自動リサイズする hook。
 * @param value textarea の現在の値
 * @param maxLines 最大行数 (デフォルト: 3)。超過時は overflow-y: auto でスクロール
 */
export function useAutoResize(value: string, maxLines = 3) {
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const style = getComputedStyle(el);
    const lineHeight = parseFloat(style.lineHeight);
    const paddingY = parseFloat(style.paddingTop) + parseFloat(style.paddingBottom);
    const maxHeight = lineHeight * maxLines + paddingY;
    el.style.height = "auto";
    const next = Math.min(el.scrollHeight, maxHeight);
    el.style.height = `${next}px`;
    el.style.overflowY = el.scrollHeight > maxHeight ? "auto" : "hidden";
  }, [value, maxLines]);

  return ref;
}
