import { renderHook, act } from "@testing-library/react";
import { useIndexForm } from "./useIndexForm";

jest.mock("react", () => ({
  ...jest.requireActual("react"),
  useActionState: (action: unknown, initialState: unknown) => [
    initialState,
    action,
  ],
}));

jest.mock("@/app/(main)/index/actions", () => ({
  indexDocument: jest.fn(),
}));

jest.mock("@/lib/api", () => ({
  checkIndexHealth: jest.fn(),
}));

describe("useIndexForm", () => {
  it("初期状態が正しい", () => {
    const { result } = renderHook(() => useIndexForm());

    expect(result.current.activeTab).toBe("text");
    expect(result.current.fileContent).toBe("");
    expect(result.current.fileName).toBe("");
    expect(result.current.healthStatus).toBe("idle");
    expect(result.current.health).toBeNull();
  });

  it("タブを切り替えられる", () => {
    const { result } = renderHook(() => useIndexForm());

    act(() => {
      result.current.setActiveTab("file");
    });

    expect(result.current.activeTab).toBe("file");
  });

  it("ヘルスチェック成功時に ok になる", async () => {
    const { checkIndexHealth } = require("@/lib/api");
    checkIndexHealth.mockResolvedValueOnce({ llm: true, embedding: true, ok: true });

    const { result } = renderHook(() => useIndexForm());

    await act(async () => {
      await result.current.handleHealthCheck();
    });

    expect(result.current.healthStatus).toBe("ok");
    expect(result.current.health).toEqual({ llm: true, embedding: true, ok: true });
  });

  it("ヘルスチェック失敗時に error になる", async () => {
    const { checkIndexHealth } = require("@/lib/api");
    checkIndexHealth.mockResolvedValueOnce({ llm: false, embedding: true, ok: false });

    const { result } = renderHook(() => useIndexForm());

    await act(async () => {
      await result.current.handleHealthCheck();
    });

    expect(result.current.healthStatus).toBe("error");
    expect(result.current.health?.llm).toBe(false);
  });
});
