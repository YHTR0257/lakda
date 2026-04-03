"use client";

import { useActionState } from "react";
import { indexDocument } from "@/app/index/actions";
import { checkIndexHealth } from "@/lib/api";
import { useEffect, useRef, useState } from "react";
import type { LlmHealthResponse } from "@/types/index";

export type Tab = "text" | "file";
export type HealthStatus = "idle" | "checking" | "ok" | "error";

const initialState = {
  success: false,
  doc_id: null as string | null,
  timestamp: "",
  error: "",
};

export function useIndexForm() {
  const [state, formAction] = useActionState(indexDocument, initialState);
  const [activeTab, setActiveTab] = useState<Tab>("text");
  const [fileContent, setFileContent] = useState<string>("");
  const [fileName, setFileName] = useState<string>("");
  const [healthStatus, setHealthStatus] = useState<HealthStatus>("idle");
  const [health, setHealth] = useState<LlmHealthResponse | null>(null);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (state.success) {
      formRef.current?.reset();
      setFileContent("");
      setFileName("");
    }
  }, [state.success]);

  async function handleHealthCheck() {
    setHealthStatus("checking");
    try {
      const result = await checkIndexHealth();
      setHealth(result);
      setHealthStatus(result.ok ? "ok" : "error");
    } catch {
      setHealth({ llm: false, embedding: false, ok: false });
      setHealthStatus("error");
    }
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);

    if (file.name.endsWith(".md") || file.type === "text/markdown") {
      const reader = new FileReader();
      reader.onload = (event) => {
        setFileContent(event.target?.result as string);
      };
      reader.readAsText(file);
    } else {
      setFileContent("");
    }
  }

  return {
    state,
    formAction,
    formRef,
    activeTab,
    setActiveTab,
    fileContent,
    fileName,
    handleFileChange,
    healthStatus,
    health,
    handleHealthCheck,
  };
}
