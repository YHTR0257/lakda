import { renderHook, act } from "@testing-library/react";
import { useAskForm } from "./useAskForm";

// confirmQuestion action をモック
jest.mock("@/app/ask/actions", () => ({
  confirmQuestion: jest.fn(),
}));

// useActionState をモック
jest.mock("react", () => ({
  ...jest.requireActual("react"),
  useActionState: jest.fn((action: unknown, initial: unknown) => [initial, action]),
}));

describe("useAskForm", () => {
  it("初期状態が正しいこと", () => {
    const { result } = renderHook(() => useAskForm());
    expect(result.current.state.success).toBe(false);
    expect(result.current.state.answer).toBeNull();
    expect(result.current.state.error).toBe("");
  });

  it("formAction と formRef を返すこと", () => {
    const { result } = renderHook(() => useAskForm());
    expect(typeof result.current.formAction).toBe("function");
    expect(result.current.formRef).toBeDefined();
  });
});
